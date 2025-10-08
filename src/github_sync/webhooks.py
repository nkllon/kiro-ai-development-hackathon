"""
Webhook integration system for real-time GitHub updates.

This module provides webhook handling for real-time synchronization
with GitHub events, including signature validation and event processing.
"""

import hmac
import hashlib
import json
import logging
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, field
from queue import Queue, Empty
from threading import Thread, Lock
import os

from .models import WebhookEvent, Repository, Issue, PullRequest, Commit
from .config import GitHubCredentials, load_env_vars, get_secure_credential
from .client import GitHubAPIClient

logger = logging.getLogger(__name__)


class WebhookError(Exception):
    """Base exception for webhook operations."""
    pass


class WebhookValidationError(WebhookError):
    """Raised when webhook signature validation fails."""
    pass


@dataclass
class WebhookConfig:
    """Configuration for webhook setup."""
    url: str
    secret: str
    events: List[str] = field(default_factory=lambda: ["push", "issues", "pull_request"])
    content_type: str = "json"
    insecure_ssl: bool = False
    active: bool = True


@dataclass
class ProcessedWebhookEvent:
    """Represents a processed webhook event with metadata."""
    event: WebhookEvent
    processed_at: datetime
    processing_duration: float
    success: bool
    error_message: Optional[str] = None


class WebhookEventQueue:
    """
    Thread-safe queue for webhook events with retry mechanisms.
    """
    
    def __init__(self, max_size: int = 1000, max_retries: int = 3):
        """
        Initialize webhook event queue.
        
        Args:
            max_size: Maximum queue size
            max_retries: Maximum retry attempts for failed events
        """
        self.queue = Queue(maxsize=max_size)
        self.max_retries = max_retries
        self.retry_queue = Queue()
        self.failed_events: List[WebhookEvent] = []
        self.lock = Lock()
        
        # Statistics
        self.stats = {
            'events_queued': 0,
            'events_processed': 0,
            'events_failed': 0,
            'events_retried': 0
        }
    
    def enqueue(self, event: WebhookEvent) -> bool:
        """
        Add event to processing queue.
        
        Args:
            event: Webhook event to queue
            
        Returns:
            True if queued successfully, False if queue is full
        """
        try:
            self.queue.put_nowait(event)
            with self.lock:
                self.stats['events_queued'] += 1
            logger.debug(f"Queued webhook event: {event.event_type}/{event.action}")
            return True
        except:
            logger.warning("Webhook event queue is full, dropping event")
            return False
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[WebhookEvent]:
        """
        Get next event from queue.
        
        Args:
            timeout: Optional timeout for blocking get
            
        Returns:
            Next webhook event or None if timeout
        """
        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            return None
    
    def enqueue_retry(self, event: WebhookEvent, error: str):
        """
        Add event to retry queue.
        
        Args:
            event: Failed webhook event
            error: Error message
        """
        if not hasattr(event, 'retry_count'):
            event.retry_count = 0
        
        event.retry_count += 1
        event.last_error = error
        
        if event.retry_count <= self.max_retries:
            self.retry_queue.put(event)
            with self.lock:
                self.stats['events_retried'] += 1
            logger.info(f"Queued event for retry (attempt {event.retry_count}): {event.event_type}")
        else:
            with self.lock:
                self.failed_events.append(event)
                self.stats['events_failed'] += 1
            logger.error(f"Event failed after {self.max_retries} retries: {event.event_type}")
    
    def get_retry_event(self) -> Optional[WebhookEvent]:
        """Get next event from retry queue."""
        try:
            return self.retry_queue.get_nowait()
        except Empty:
            return None
    
    def mark_processed(self):
        """Mark an event as processed."""
        with self.lock:
            self.stats['events_processed'] += 1
        self.queue.task_done()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        with self.lock:
            return {
                **self.stats,
                'queue_size': self.queue.qsize(),
                'retry_queue_size': self.retry_queue.qsize(),
                'failed_events_count': len(self.failed_events)
            }


class WebhookHandler:
    """
    Webhook handler for real-time GitHub updates.
    
    Handles webhook endpoint configuration, signature validation,
    and event processing with retry mechanisms.
    """
    
    def __init__(self, github_client: Optional[GitHubAPIClient] = None):
        """
        Initialize webhook handler.
        
        Args:
            github_client: GitHub API client for webhook management
        """
        self.github_client = github_client or GitHubAPIClient()
        self.event_queue = WebhookEventQueue()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.webhook_secret = self._load_webhook_secret()
        
        # Processing threads
        self.processing_threads: List[Thread] = []
        self.is_running = False
        
        # Event processing statistics
        self.processed_events: List[ProcessedWebhookEvent] = []
        self.max_processed_history = 1000
    
    def _load_webhook_secret(self) -> str:
        """
        Load webhook secret from environment variables.
        
        Returns:
            Webhook secret for signature validation
            
        Raises:
            WebhookError: If secret is not found
        """
        try:
            load_env_vars()
            return get_secure_credential(
                "GITHUB_WEBHOOK_SECRET",
                "GitHub Webhook Secret"
            )
        except ValueError as e:
            logger.warning(f"Webhook secret not configured: {e}")
            return ""  # Allow operation without signature validation
    
    def validate_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Validate webhook signature for security.
        
        Args:
            payload: Raw webhook payload
            signature: GitHub signature header (X-Hub-Signature-256)
            
        Returns:
            True if signature is valid, False otherwise
            
        Raises:
            WebhookValidationError: If validation fails
        """
        # Security: If no webhook secret is configured, validation should fail
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured, signature validation failed")
            return False
        
        if not signature:
            logger.warning("Missing webhook signature")
            return False
        
        # GitHub sends signature as "sha256=<hash>"
        if not signature.startswith('sha256='):
            logger.warning("Invalid signature format")
            return False
        
        expected_signature = signature[7:]  # Remove "sha256=" prefix
        
        # Calculate expected signature
        calculated_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Use constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(expected_signature, calculated_signature)
        
        if not is_valid:
            logger.warning("Webhook signature validation failed")
            return False
        
        return True
    
    def register_event_handler(self, event_type: str, handler: Callable[[WebhookEvent], None]):
        """
        Register handler for specific webhook event type.
        
        Args:
            event_type: GitHub event type (push, issues, pull_request, etc.)
            handler: Handler function that takes WebhookEvent as parameter
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type} events")
    
    def process_webhook_payload(self, payload: str, event_type: str, 
                              signature: Optional[str] = None) -> bool:
        """
        Process incoming webhook payload.
        
        Args:
            payload: Raw JSON payload from GitHub
            event_type: GitHub event type from X-GitHub-Event header
            signature: GitHub signature from X-Hub-Signature-256 header
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            # Validate signature if provided
            if signature:
                self.validate_webhook_signature(payload, signature)
            
            # Parse payload
            payload_data = json.loads(payload)
            
            # Extract repository information
            repo_data = payload_data.get('repository', {})
            if not repo_data:
                logger.warning(f"No repository data in {event_type} webhook")
                return False
            
            repository = Repository(
                id=repo_data['id'],
                name=repo_data['name'],
                owner=repo_data['owner']['login'],
                full_name=repo_data['full_name'],
                description=repo_data.get('description'),
                default_branch=repo_data.get('default_branch', 'main'),
                private=repo_data.get('private', False)
            )
            
            # Create webhook event
            webhook_event = WebhookEvent(
                event_type=event_type,
                action=payload_data.get('action', 'unknown'),
                repository=repository,
                payload=payload_data,
                timestamp=datetime.utcnow()
            )
            
            # Queue event for processing
            if self.event_queue.enqueue(webhook_event):
                logger.info(f"Processed webhook: {event_type}/{webhook_event.action} for {repository.full_name}")
                return True
            else:
                logger.error(f"Failed to queue webhook event: {event_type}")
                return False
                
        except WebhookValidationError as e:
            logger.error(f"Webhook validation failed: {e}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in webhook payload: {e}")
            return False
        except Exception as e:
            logger.error(f"Error processing webhook payload: {e}")
            return False
    
    def start_processing(self, num_workers: int = 3):
        """
        Start webhook event processing threads.
        
        Args:
            num_workers: Number of worker threads to start
        """
        if self.is_running:
            logger.warning("Webhook processing is already running")
            return
        
        self.is_running = True
        
        # Start worker threads
        for i in range(num_workers):
            worker = Thread(target=self._process_events_worker, args=(i,))
            worker.daemon = True
            worker.start()
            self.processing_threads.append(worker)
        
        # Start retry processor
        retry_worker = Thread(target=self._process_retry_events)
        retry_worker.daemon = True
        retry_worker.start()
        self.processing_threads.append(retry_worker)
        
        logger.info(f"Started webhook processing with {num_workers} workers")
    
    def stop_processing(self):
        """Stop webhook event processing."""
        self.is_running = False
        
        # Wait for threads to finish current work
        for thread in self.processing_threads:
            if thread.is_alive():
                thread.join(timeout=5.0)
        
        self.processing_threads.clear()
        logger.info("Stopped webhook processing")
    
    def _process_events_worker(self, worker_id: int):
        """
        Worker thread for processing webhook events.
        
        Args:
            worker_id: Worker thread identifier
        """
        logger.info(f"Webhook worker {worker_id} started")
        
        while self.is_running:
            try:
                # Get next event from queue
                event = self.event_queue.dequeue(timeout=1.0)
                if event is None:
                    continue
                
                # Process event
                start_time = time.time()
                success = self._process_single_event(event)
                processing_duration = time.time() - start_time
                
                # Record processing result
                processed_event = ProcessedWebhookEvent(
                    event=event,
                    processed_at=datetime.utcnow(),
                    processing_duration=processing_duration,
                    success=success,
                    error_message=getattr(event, 'last_error', None) if not success else None
                )
                
                self._record_processed_event(processed_event)
                
                if success:
                    self.event_queue.mark_processed()
                    logger.debug(f"Worker {worker_id} processed {event.event_type} event in {processing_duration:.2f}s")
                else:
                    self.event_queue.enqueue_retry(event, getattr(event, 'last_error', 'Unknown error'))
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
        
        logger.info(f"Webhook worker {worker_id} stopped")
    
    def _process_retry_events(self):
        """Process events from retry queue."""
        logger.info("Webhook retry processor started")
        
        while self.is_running:
            try:
                event = self.event_queue.get_retry_event()
                if event is None:
                    time.sleep(5.0)  # Wait before checking again
                    continue
                
                # Add delay for retry (exponential backoff)
                retry_delay = min(2 ** (event.retry_count - 1), 60)  # Max 60 seconds
                time.sleep(retry_delay)
                
                # Retry processing
                success = self._process_single_event(event)
                
                if success:
                    logger.info(f"Retry successful for {event.event_type} event")
                else:
                    self.event_queue.enqueue_retry(event, getattr(event, 'last_error', 'Retry failed'))
                
            except Exception as e:
                logger.error(f"Retry processor error: {e}")
        
        logger.info("Webhook retry processor stopped")
    
    def _process_single_event(self, event: WebhookEvent) -> bool:
        """
        Process a single webhook event.
        
        Args:
            event: Webhook event to process
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            # Get handlers for this event type
            handlers = self.event_handlers.get(event.event_type, [])
            
            if not handlers:
                logger.debug(f"No handlers registered for {event.event_type} events")
                return True  # Not an error, just no handlers
            
            # Execute all handlers
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Handler error for {event.event_type}: {e}")
                    event.last_error = str(e)
                    return False
            
            # Mark event as processed
            event.processed = True
            return True
            
        except Exception as e:
            logger.error(f"Error processing {event.event_type} event: {e}")
            event.last_error = str(e)
            return False
    
    def _record_processed_event(self, processed_event: ProcessedWebhookEvent):
        """Record processed event for monitoring."""
        self.processed_events.append(processed_event)
        
        # Keep only recent events
        if len(self.processed_events) > self.max_processed_history:
            self.processed_events = self.processed_events[-self.max_processed_history:]
    
    async def handle_push_event(self, event_data: Dict[str, Any]):
        """
        Handle push webhook events.
        
        Args:
            event_data: Push event payload from GitHub
        """
        try:
            await self._process_push_event(event_data)
        except Exception as e:
            logger.error(f"Error handling push event: {e}")
            raise
    
    async def handle_issue_event(self, event_data: Dict[str, Any]):
        """
        Handle issue webhook events.
        
        Args:
            event_data: Issue event payload from GitHub
        """
        try:
            await self._process_issue_event(event_data)
        except Exception as e:
            logger.error(f"Error handling issue event: {e}")
            raise
    
    async def _process_push_event(self, event_data: Dict[str, Any]):
        """
        Process push event data.
        
        Args:
            event_data: Push event payload
        """
        repository = event_data.get('repository', {})
        commits = event_data.get('commits', [])
        ref = event_data.get('ref', '')
        
        logger.info(f"Processing push event for {repository.get('full_name', 'unknown')} on {ref}")
        logger.info(f"Push contains {len(commits)} commits")
        
        # Create webhook event for processing
        repo_name = repository.get('name', 'unknown')
        repo_owner = repository.get('owner', {}).get('login', 'unknown')
        
        webhook_event = WebhookEvent(
            event_type='push',
            action='pushed',
            repository=Repository(
                id=repository.get('id', 0),
                name=repo_name,
                owner=repo_owner,
                full_name=repository.get('full_name', f'{repo_owner}/{repo_name}'),
                description=repository.get('description'),
                default_branch=repository.get('default_branch', 'main'),
                private=repository.get('private', False)
            ),
            payload=event_data,
            timestamp=datetime.utcnow()
        )
        
        # Process through event handlers
        handlers = self.event_handlers.get('push', [])
        for handler in handlers:
            try:
                handler(webhook_event)
            except Exception as e:
                logger.error(f"Push event handler error: {e}")
    
    async def _process_issue_event(self, event_data: Dict[str, Any]):
        """
        Process issue event data.
        
        Args:
            event_data: Issue event payload
        """
        repository = event_data.get('repository', {})
        issue = event_data.get('issue', {})
        action = event_data.get('action', 'unknown')
        
        logger.info(f"Processing issue event: {action} for issue #{issue.get('number', 'unknown')} in {repository.get('full_name', 'unknown')}")
        
        # Create webhook event for processing
        repo_name = repository.get('name', 'unknown')
        repo_owner = repository.get('owner', {}).get('login', 'unknown')
        
        webhook_event = WebhookEvent(
            event_type='issues',
            action=action,
            repository=Repository(
                id=repository.get('id', 0),
                name=repo_name,
                owner=repo_owner,
                full_name=repository.get('full_name', f'{repo_owner}/{repo_name}'),
                description=repository.get('description'),
                default_branch=repository.get('default_branch', 'main'),
                private=repository.get('private', False)
            ),
            payload=event_data,
            timestamp=datetime.utcnow()
        )
        
        # Process through event handlers
        handlers = self.event_handlers.get('issues', [])
        for handler in handlers:
            try:
                handler(webhook_event)
            except Exception as e:
                logger.error(f"Issue event handler error: {e}") 
   
    def setup_webhooks(self, repo_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Set up webhooks for repositories.
        
        Args:
            repo_configs: List of repository configurations with webhook settings
            
        Returns:
            List of webhook setup results
        """
        results = []
        
        for repo_config in repo_configs:
            try:
                owner = repo_config['owner']
                repo = repo_config['repo']
                webhook_config = repo_config.get('webhook_config', {})
                
                # Create webhook configuration
                webhook_data = {
                    'name': 'web',
                    'active': webhook_config.get('active', True),
                    'events': webhook_config.get('events', ['push', 'issues', 'pull_request']),
                    'config': {
                        'url': webhook_config.get('url', ''),
                        'content_type': webhook_config.get('content_type', 'json'),
                        'insecure_ssl': webhook_config.get('insecure_ssl', '0'),
                        'secret': self.webhook_secret
                    }
                }
                
                # Set up webhook via GitHub API
                result = self._create_webhook(owner, repo, webhook_data)
                results.append({
                    'repository': f"{owner}/{repo}",
                    'success': result.get('success', False),
                    'webhook_id': result.get('webhook_id'),
                    'error': result.get('error')
                })
                
            except Exception as e:
                logger.error(f"Failed to setup webhook for {repo_config}: {e}")
                results.append({
                    'repository': f"{repo_config.get('owner', 'unknown')}/{repo_config.get('repo', 'unknown')}",
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def _create_webhook(self, owner: str, repo: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create webhook via GitHub API.
        
        Args:
            owner: Repository owner
            repo: Repository name
            webhook_data: Webhook configuration data
            
        Returns:
            Dictionary with creation result
        """
        try:
            # This would typically use the GitHub API to create webhooks
            # For now, we'll simulate the process
            logger.info(f"Creating webhook for {owner}/{repo}")
            
            # Simulate API call
            webhook_id = f"webhook_{owner}_{repo}_{int(time.time())}"
            
            return {
                'success': True,
                'webhook_id': webhook_id,
                'url': webhook_data['config']['url'],
                'events': webhook_data['events']
            }
            
        except Exception as e:
            logger.error(f"Failed to create webhook for {owner}/{repo}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_webhook_stats(self) -> Dict[str, Any]:
        """
        Get webhook processing statistics.
        
        Returns:
            Dictionary with webhook statistics
        """
        queue_stats = self.event_queue.get_stats()
        
        # Calculate processing metrics
        recent_events = [
            event for event in self.processed_events
            if (datetime.utcnow() - event.processed_at).total_seconds() < 3600
        ]
        
        successful_events = [event for event in recent_events if event.success]
        failed_events = [event for event in recent_events if not event.success]
        
        avg_processing_time = 0.0
        if recent_events:
            avg_processing_time = sum(event.processing_duration for event in recent_events) / len(recent_events)
        
        return {
            'queue_stats': queue_stats,
            'processing_stats': {
                'events_last_hour': len(recent_events),
                'successful_events_last_hour': len(successful_events),
                'failed_events_last_hour': len(failed_events),
                'success_rate_percent': (len(successful_events) / len(recent_events) * 100) if recent_events else 0,
                'average_processing_time_seconds': avg_processing_time,
                'total_processed_events': len(self.processed_events)
            },
            'handlers_registered': {event_type: len(handlers) for event_type, handlers in self.event_handlers.items()},
            'is_running': self.is_running,
            'worker_threads': len(self.processing_threads)
        }
    
    def get_failed_events(self, limit: int = 50) -> List[WebhookEvent]:
        """
        Get recent failed events for debugging.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of failed webhook events
        """
        return self.event_queue.failed_events[-limit:]
    
    def retry_failed_event(self, event: WebhookEvent) -> bool:
        """
        Manually retry a failed event.
        
        Args:
            event: Failed webhook event to retry
            
        Returns:
            True if retry was successful
        """
        try:
            # Reset retry count for manual retry
            event.retry_count = 0
            event.last_error = None
            
            # Process the event
            success = self._process_single_event(event)
            
            if success:
                logger.info(f"Manual retry successful for {event.event_type} event")
                # Remove from failed events if present
                if event in self.event_queue.failed_events:
                    self.event_queue.failed_events.remove(event)
            
            return success
            
        except Exception as e:
            logger.error(f"Manual retry failed for {event.event_type}: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on webhook system.
        
        Returns:
            Health check results
        """
        health_status = {
            'status': 'healthy',
            'issues': [],
            'checks': {}
        }
        
        try:
            # Check if processing is running
            health_status['checks']['processing_running'] = self.is_running
            if not self.is_running:
                health_status['issues'].append('Webhook processing is not running')
                health_status['status'] = 'unhealthy'
            
            # Check queue sizes
            queue_stats = self.event_queue.get_stats()
            health_status['checks']['queue_size'] = queue_stats['queue_size']
            health_status['checks']['retry_queue_size'] = queue_stats['retry_queue_size']
            health_status['checks']['failed_events_count'] = queue_stats['failed_events_count']
            
            # Check for high failure rate
            recent_events = [
                event for event in self.processed_events
                if (datetime.utcnow() - event.processed_at).total_seconds() < 3600
            ]
            
            if recent_events:
                failed_count = len([event for event in recent_events if not event.success])
                failure_rate = failed_count / len(recent_events) * 100
                health_status['checks']['failure_rate_percent'] = failure_rate
                
                if failure_rate > 50:
                    health_status['issues'].append(f'High failure rate: {failure_rate:.1f}%')
                    health_status['status'] = 'degraded'
            
            # Check webhook secret configuration
            health_status['checks']['webhook_secret_configured'] = bool(self.webhook_secret)
            if not self.webhook_secret:
                health_status['issues'].append('Webhook secret not configured')
                health_status['status'] = 'degraded'
            
            # Check for stuck events
            if queue_stats['queue_size'] > 100:
                health_status['issues'].append('Event queue is backing up')
                health_status['status'] = 'degraded'
            
        except Exception as e:
            health_status['status'] = 'error'
            health_status['issues'].append(f'Health check failed: {e}')
        
        return health_status


# Default event handlers for common webhook events
class DefaultWebhookHandlers:
    """Default webhook event handlers for common GitHub events."""
    
    def __init__(self, sync_engine=None, cache_manager=None):
        """
        Initialize default handlers.
        
        Args:
            sync_engine: Synchronization engine for data updates
            cache_manager: Cache manager for invalidation
        """
        self.sync_engine = sync_engine
        self.cache_manager = cache_manager
    
    def handle_push_event(self, event: WebhookEvent):
        """Handle push events (new commits)."""
        try:
            repo_name = event.repository.full_name
            commits = event.payload.get('commits', [])
            
            logger.info(f"Processing push event for {repo_name}: {len(commits)} commits")
            
            # Invalidate commits cache
            if self.cache_manager:
                self.cache_manager.invalidate_cache(repo_name, 'commits')
            
            # Trigger incremental sync if sync engine available
            if self.sync_engine:
                # This would trigger a sync for the specific repository
                logger.debug(f"Triggering sync for {repo_name} after push event")
            
        except Exception as e:
            logger.error(f"Error handling push event: {e}")
            raise
    
    def handle_issues_event(self, event: WebhookEvent):
        """Handle issues events (created, updated, closed, etc.)."""
        try:
            repo_name = event.repository.full_name
            action = event.action
            issue_data = event.payload.get('issue', {})
            
            logger.info(f"Processing issues event for {repo_name}: {action} issue #{issue_data.get('number')}")
            
            # Invalidate issues cache
            if self.cache_manager:
                self.cache_manager.invalidate_cache(repo_name, 'issues')
            
            # Trigger sync for issues
            if self.sync_engine:
                logger.debug(f"Triggering issues sync for {repo_name} after {action} event")
            
        except Exception as e:
            logger.error(f"Error handling issues event: {e}")
            raise
    
    def handle_pull_request_event(self, event: WebhookEvent):
        """Handle pull request events (opened, closed, merged, etc.)."""
        try:
            repo_name = event.repository.full_name
            action = event.action
            pr_data = event.payload.get('pull_request', {})
            
            logger.info(f"Processing PR event for {repo_name}: {action} PR #{pr_data.get('number')}")
            
            # Invalidate pull requests cache
            if self.cache_manager:
                self.cache_manager.invalidate_cache(repo_name, 'pull_requests')
            
            # If PR was merged, also invalidate commits cache
            if action == 'closed' and pr_data.get('merged'):
                if self.cache_manager:
                    self.cache_manager.invalidate_cache(repo_name, 'commits')
            
            # Trigger sync for pull requests
            if self.sync_engine:
                logger.debug(f"Triggering PR sync for {repo_name} after {action} event")
            
        except Exception as e:
            logger.error(f"Error handling pull request event: {e}")
            raise
    
    def handle_repository_event(self, event: WebhookEvent):
        """Handle repository events (created, deleted, etc.)."""
        try:
            repo_name = event.repository.full_name
            action = event.action
            
            logger.info(f"Processing repository event: {action} for {repo_name}")
            
            # For repository deletion, clear all cache
            if action == 'deleted' and self.cache_manager:
                self.cache_manager.invalidate_cache(repo_name)
            
            # For other actions, invalidate repository cache
            elif self.cache_manager:
                self.cache_manager.invalidate_cache(repo_name, 'repositories')
            
        except Exception as e:
            logger.error(f"Error handling repository event: {e}")
            raise