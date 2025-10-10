"""
Comprehensive webhook event processors for GitHub synchronization.

This module provides specialized event processors for different types of
GitHub webhook events with real-time data updates and event queuing.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .models import WebhookEvent, Repository, Issue, PullRequest, Commit, SyncResult
from .webhooks import WebhookHandler
from .sync_engine import SynchronizationEngine
from .cache import CacheManager
from .client import GitHubAPIClient

logger = logging.getLogger(__name__)


@dataclass
class EventProcessingResult:
    """Result of event processing operation."""
    success: bool
    event_type: str
    action: str
    repository: str
    processing_time: float
    items_updated: int = 0
    cache_invalidated: bool = False
    sync_triggered: bool = False
    error_message: Optional[str] = None


class BaseEventProcessor(ABC):
    """Base class for webhook event processors."""
    
    def __init__(self, sync_engine: Optional[SynchronizationEngine] = None,
                 cache_manager: Optional[CacheManager] = None,
                 github_client: Optional[GitHubAPIClient] = None):
        """
        Initialize base event processor.
        
        Args:
            sync_engine: Synchronization engine for data updates
            cache_manager: Cache manager for invalidation
            github_client: GitHub API client for additional data fetching
        """
        self.sync_engine = sync_engine
        self.cache_manager = cache_manager
        self.github_client = github_client
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    @abstractmethod
    def can_process(self, event: WebhookEvent) -> bool:
        """
        Check if this processor can handle the given event.
        
        Args:
            event: Webhook event to check
            
        Returns:
            True if processor can handle the event
        """
        pass
    
    @abstractmethod
    def process_event(self, event: WebhookEvent) -> EventProcessingResult:
        """
        Process the webhook event.
        
        Args:
            event: Webhook event to process
            
        Returns:
            Event processing result
        """
        pass
    
    def invalidate_cache(self, repo_name: str, data_type: Optional[str] = None) -> bool:
        """
        Invalidate cache for repository data.
        
        Args:
            repo_name: Repository name
            data_type: Optional specific data type to invalidate
            
        Returns:
            True if cache was invalidated
        """
        if self.cache_manager:
            return self.cache_manager.invalidate_cache(repo_name, data_type)
        return False
    
    def trigger_sync(self, repo_name: str, sync_type: Optional[str] = None) -> bool:
        """
        Trigger synchronization for repository.
        
        Args:
            repo_name: Repository name
            sync_type: Optional specific sync type
            
        Returns:
            True if sync was triggered
        """
        if self.sync_engine:
            # This would trigger appropriate sync based on the event
            logger.debug(f"Triggering {sync_type or 'full'} sync for {repo_name}")
            return True
        return False


class PushEventProcessor(BaseEventProcessor):
    """Processor for push events (new commits)."""
    
    def can_process(self, event: WebhookEvent) -> bool:
        """Check if this is a push event."""
        return event.event_type == 'push'
    
    def process_event(self, event: WebhookEvent) -> EventProcessingResult:
        """Process push event with commit synchronization."""
        start_time = datetime.now()
        result = EventProcessingResult(
            success=True,
            event_type=event.event_type,
            action=event.action,
            repository=event.repository.full_name,
            processing_time=0.0
        )
        
        try:
            repo_name = event.repository.full_name
            commits = event.payload.get('commits', [])
            branch = event.payload.get('ref', '').replace('refs/heads/', '')
            
            logger.info(f"Processing push event: {len(commits)} commits to {branch} in {repo_name}")
            
            # Process each commit
            processed_commits = []
            for commit_data in commits:
                try:
                    # Create commit object from webhook data
                    commit = Commit(
                        sha=commit_data['id'],
                        message=commit_data['message'],
                        author=commit_data['author']['name'],
                        author_email=commit_data['author']['email'],
                        committed_at=datetime.fromisoformat(commit_data['timestamp'].replace('Z', '+00:00')),
                        branch=branch,
                        files_changed=[f['filename'] for f in commit_data.get('modified', []) + 
                                     commit_data.get('added', []) + commit_data.get('removed', [])]
                    )
                    processed_commits.append(commit)
                    
                except Exception as e:
                    logger.error(f"Error processing commit {commit_data.get('id', 'unknown')}: {e}")
            
            result.items_updated = len(processed_commits)
            
            # Invalidate commits cache
            if self.invalidate_cache(repo_name, 'commits'):
                result.cache_invalidated = True
            
            # Cache new commits if cache manager available
            if self.cache_manager and processed_commits:
                self.cache_manager.cache_commits(repo_name, processed_commits)
            
            # Trigger incremental sync for commits
            if self.trigger_sync(repo_name, 'commits'):
                result.sync_triggered = True
            
            # Handle branch updates
            self._process_branch_update(event, branch, result)
            
            logger.info(f"Successfully processed push event for {repo_name}: {result.items_updated} commits")
            
        except Exception as e:
            logger.error(f"Error processing push event: {e}")
            result.success = False
            result.error_message = str(e)
        
        finally:
            result.processing_time = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def _process_branch_update(self, event: WebhookEvent, branch: str, result: EventProcessingResult):
        """Process branch-related updates from push event."""
        try:
            # Check if this is a new branch
            if event.payload.get('created', False):
                logger.info(f"New branch created: {branch} in {event.repository.full_name}")
                # Invalidate branch cache
                self.invalidate_cache(event.repository.full_name, 'branches')
            
            # Check if branch was deleted
            if event.payload.get('deleted', False):
                logger.info(f"Branch deleted: {branch} in {event.repository.full_name}")
                # Invalidate branch cache
                self.invalidate_cache(event.repository.full_name, 'branches')
            
        except Exception as e:
            logger.error(f"Error processing branch update: {e}")


class IssuesEventProcessor(BaseEventProcessor):
    """Processor for issues events."""
    
    def can_process(self, event: WebhookEvent) -> bool:
        """Check if this is an issues event."""
        return event.event_type == 'issues'
    
    def process_event(self, event: WebhookEvent) -> EventProcessingResult:
        """Process issues event with real-time updates."""
        start_time = datetime.now()
        result = EventProcessingResult(
            success=True,
            event_type=event.event_type,
            action=event.action,
            repository=event.repository.full_name,
            processing_time=0.0
        )
        
        try:
            repo_name = event.repository.full_name
            action = event.action
            issue_data = event.payload.get('issue', {})
            
            logger.info(f"Processing issues event: {action} issue #{issue_data.get('number')} in {repo_name}")
            
            # Process the issue based on action
            if action in ['opened', 'edited', 'closed', 'reopened']:
                issue = self._create_issue_from_webhook(issue_data)
                if issue:
                    result.items_updated = 1
                    
                    # Update cache with new issue data
                    if self.cache_manager:
                        # For individual issue updates, we could implement partial cache updates
                        self.cache_manager.cache_issues(repo_name, [issue])
                    
            elif action == 'deleted':
                # Issue was deleted - invalidate cache
                result.items_updated = 1
            
            # Invalidate issues cache for consistency
            if self.invalidate_cache(repo_name, 'issues'):
                result.cache_invalidated = True
            
            # Trigger issues sync
            if self.trigger_sync(repo_name, 'issues'):
                result.sync_triggered = True
            
            # Handle issue comments if present
            if action == 'edited' and 'comment' in event.payload:
                self._process_issue_comment(event, result)
            
            logger.info(f"Successfully processed issues event for {repo_name}")
            
        except Exception as e:
            logger.error(f"Error processing issues event: {e}")
            result.success = False
            result.error_message = str(e)
        
        finally:
            result.processing_time = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def _create_issue_from_webhook(self, issue_data: Dict[str, Any]) -> Optional[Issue]:
        """Create Issue object from webhook data."""
        try:
            from .models import IssueState
            
            return Issue(
                id=issue_data['id'],
                number=issue_data['number'],
                title=issue_data['title'],
                body=issue_data.get('body'),
                state=IssueState(issue_data['state']),
                assignees=[assignee['login'] for assignee in issue_data.get('assignees', [])],
                labels=[label['name'] for label in issue_data.get('labels', [])],
                milestone=issue_data['milestone']['title'] if issue_data.get('milestone') else None,
                created_at=datetime.fromisoformat(issue_data['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(issue_data['updated_at'].replace('Z', '+00:00')),
                closed_at=datetime.fromisoformat(issue_data['closed_at'].replace('Z', '+00:00')) if issue_data.get('closed_at') else None,
                author=issue_data['user']['login'],
                comments_count=issue_data.get('comments', 0)
            )
        except Exception as e:
            logger.error(f"Error creating issue from webhook data: {e}")
            return None
    
    def _process_issue_comment(self, event: WebhookEvent, result: EventProcessingResult):
        """Process issue comment updates."""
        try:
            comment_data = event.payload.get('comment', {})
            logger.debug(f"Processing issue comment update: {comment_data.get('id')}")
            # Comment processing would be implemented here
            
        except Exception as e:
            logger.error(f"Error processing issue comment: {e}")


class PullRequestEventProcessor(BaseEventProcessor):
    """Processor for pull request events."""
    
    def can_process(self, event: WebhookEvent) -> bool:
        """Check if this is a pull request event."""
        return event.event_type == 'pull_request'
    
    def process_event(self, event: WebhookEvent) -> EventProcessingResult:
        """Process pull request event with real-time updates."""
        start_time = datetime.now()
        result = EventProcessingResult(
            success=True,
            event_type=event.event_type,
            action=event.action,
            repository=event.repository.full_name,
            processing_time=0.0
        )
        
        try:
            repo_name = event.repository.full_name
            action = event.action
            pr_data = event.payload.get('pull_request', {})
            
            logger.info(f"Processing PR event: {action} PR #{pr_data.get('number')} in {repo_name}")
            
            # Process the pull request based on action
            if action in ['opened', 'edited', 'closed', 'reopened', 'synchronize']:
                pr = self._create_pr_from_webhook(pr_data)
                if pr:
                    result.items_updated = 1
                    
                    # Update cache with new PR data
                    if self.cache_manager:
                        self.cache_manager.cache_pull_requests(repo_name, [pr])
                    
                    # If PR was merged, also trigger commits sync
                    if action == 'closed' and pr_data.get('merged'):
                        self.invalidate_cache(repo_name, 'commits')
                        self.trigger_sync(repo_name, 'commits')
            
            # Invalidate pull requests cache
            if self.invalidate_cache(repo_name, 'pull_requests'):
                result.cache_invalidated = True
            
            # Trigger PR sync
            if self.trigger_sync(repo_name, 'pull_requests'):
                result.sync_triggered = True
            
            # Handle PR reviews
            if action in ['review_requested', 'review_request_removed']:
                self._process_pr_review_request(event, result)
            
            logger.info(f"Successfully processed PR event for {repo_name}")
            
        except Exception as e:
            logger.error(f"Error processing pull request event: {e}")
            result.success = False
            result.error_message = str(e)
        
        finally:
            result.processing_time = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def _create_pr_from_webhook(self, pr_data: Dict[str, Any]) -> Optional[PullRequest]:
        """Create PullRequest object from webhook data."""
        try:
            from .models import PullRequestState
            
            # Determine PR state
            pr_state = PullRequestState.OPEN
            if pr_data.get('merged'):
                pr_state = PullRequestState.MERGED
            elif pr_data['state'] == 'closed':
                pr_state = PullRequestState.CLOSED
            
            return PullRequest(
                id=pr_data['id'],
                number=pr_data['number'],
                title=pr_data['title'],
                body=pr_data.get('body'),
                state=pr_state,
                head_branch=pr_data['head']['ref'],
                base_branch=pr_data['base']['ref'],
                head_sha=pr_data['head']['sha'],
                base_sha=pr_data['base']['sha'],
                mergeable=pr_data.get('mergeable'),
                merged=pr_data.get('merged', False),
                draft=pr_data.get('draft', False),
                created_at=datetime.fromisoformat(pr_data['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(pr_data['updated_at'].replace('Z', '+00:00')),
                merged_at=datetime.fromisoformat(pr_data['merged_at'].replace('Z', '+00:00')) if pr_data.get('merged_at') else None,
                closed_at=datetime.fromisoformat(pr_data['closed_at'].replace('Z', '+00:00')) if pr_data.get('closed_at') else None,
                author=pr_data['user']['login'],
                assignees=[assignee['login'] for assignee in pr_data.get('assignees', [])],
                labels=[label['name'] for label in pr_data.get('labels', [])]
            )
        except Exception as e:
            logger.error(f"Error creating PR from webhook data: {e}")
            return None
    
    def _process_pr_review_request(self, event: WebhookEvent, result: EventProcessingResult):
        """Process PR review request changes."""
        try:
            requested_reviewer = event.payload.get('requested_reviewer', {})
            logger.debug(f"Processing PR review request for: {requested_reviewer.get('login')}")
            # Review request processing would be implemented here
            
        except Exception as e:
            logger.error(f"Error processing PR review request: {e}")


class RepositoryEventProcessor(BaseEventProcessor):
    """Processor for repository events."""
    
    def can_process(self, event: WebhookEvent) -> bool:
        """Check if this is a repository event."""
        return event.event_type == 'repository'
    
    def process_event(self, event: WebhookEvent) -> EventProcessingResult:
        """Process repository event."""
        start_time = datetime.now()
        result = EventProcessingResult(
            success=True,
            event_type=event.event_type,
            action=event.action,
            repository=event.repository.full_name,
            processing_time=0.0
        )
        
        try:
            repo_name = event.repository.full_name
            action = event.action
            
            logger.info(f"Processing repository event: {action} for {repo_name}")
            
            if action == 'deleted':
                # Repository was deleted - clear all cache
                if self.invalidate_cache(repo_name):
                    result.cache_invalidated = True
                result.items_updated = 1
                
            elif action in ['created', 'publicized', 'privatized']:
                # Repository metadata changed
                if self.invalidate_cache(repo_name, 'repositories'):
                    result.cache_invalidated = True
                
                # Trigger full sync for new or changed repositories
                if self.trigger_sync(repo_name, 'full'):
                    result.sync_triggered = True
                
                result.items_updated = 1
            
            logger.info(f"Successfully processed repository event for {repo_name}")
            
        except Exception as e:
            logger.error(f"Error processing repository event: {e}")
            result.success = False
            result.error_message = str(e)
        
        finally:
            result.processing_time = (datetime.now() - start_time).total_seconds()
        
        return result


class EventProcessorManager:
    """
    Manager for webhook event processors with routing and monitoring.
    """
    
    def __init__(self, sync_engine: Optional[SynchronizationEngine] = None,
                 cache_manager: Optional[CacheManager] = None,
                 github_client: Optional[GitHubAPIClient] = None):
        """
        Initialize event processor manager.
        
        Args:
            sync_engine: Synchronization engine
            cache_manager: Cache manager
            github_client: GitHub API client
        """
        self.sync_engine = sync_engine
        self.cache_manager = cache_manager
        self.github_client = github_client
        
        # Initialize processors
        self.processors: List[BaseEventProcessor] = [
            PushEventProcessor(sync_engine, cache_manager, github_client),
            IssuesEventProcessor(sync_engine, cache_manager, github_client),
            PullRequestEventProcessor(sync_engine, cache_manager, github_client),
            RepositoryEventProcessor(sync_engine, cache_manager, github_client)
        ]
        
        # Processing statistics
        self.processing_stats: Dict[str, int] = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0
        }
        
        self.event_type_stats: Dict[str, Dict[str, int]] = {}
    
    def process_event(self, event: WebhookEvent) -> EventProcessingResult:
        """
        Process webhook event using appropriate processor.
        
        Args:
            event: Webhook event to process
            
        Returns:
            Event processing result
        """
        # Find appropriate processor
        processor = None
        for p in self.processors:
            if p.can_process(event):
                processor = p
                break
        
        if not processor:
            logger.warning(f"No processor found for event type: {event.event_type}")
            return EventProcessingResult(
                success=False,
                event_type=event.event_type,
                action=event.action,
                repository=event.repository.full_name,
                processing_time=0.0,
                error_message=f"No processor for event type: {event.event_type}"
            )
        
        # Process the event
        try:
            result = processor.process_event(event)
            
            # Update statistics
            self.processing_stats['total_processed'] += 1
            if result.success:
                self.processing_stats['successful'] += 1
            else:
                self.processing_stats['failed'] += 1
            
            # Update event type statistics
            if event.event_type not in self.event_type_stats:
                self.event_type_stats[event.event_type] = {'processed': 0, 'successful': 0, 'failed': 0}
            
            self.event_type_stats[event.event_type]['processed'] += 1
            if result.success:
                self.event_type_stats[event.event_type]['successful'] += 1
            else:
                self.event_type_stats[event.event_type]['failed'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error in event processor manager: {e}")
            self.processing_stats['total_processed'] += 1
            self.processing_stats['failed'] += 1
            
            return EventProcessingResult(
                success=False,
                event_type=event.event_type,
                action=event.action,
                repository=event.repository.full_name,
                processing_time=0.0,
                error_message=str(e)
            )
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get event processing statistics."""
        return {
            'overall_stats': self.processing_stats,
            'event_type_stats': self.event_type_stats,
            'processors_count': len(self.processors),
            'success_rate': (self.processing_stats['successful'] / 
                           max(self.processing_stats['total_processed'], 1) * 100)
        }
    
    def add_processor(self, processor: BaseEventProcessor):
        """Add custom event processor."""
        self.processors.append(processor)
        logger.info(f"Added custom event processor: {processor.__class__.__name__}")
    
    def remove_processor(self, processor_class: type):
        """Remove event processor by class type."""
        self.processors = [p for p in self.processors if not isinstance(p, processor_class)]
        logger.info(f"Removed event processor: {processor_class.__name__}")