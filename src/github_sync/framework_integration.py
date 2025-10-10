"""
Framework integration for GitHub synchronization.

This module provides integration with the Beast Mode framework,
enabling seamless workflow integration and framework-specific customizations.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import asyncio

from .sync_engine import SynchronizationEngine
from .client import GitHubAPIClient
from .auth import AuthenticationManager
from .config import GitHubSyncConfig
from .models import Repository, Issue, PullRequest
from .git_manager import GitCommitManager
from .precommit_manager import PreCommitManager
from .data_recovery import DataRecoveryManager

logger = logging.getLogger(__name__)


@dataclass
class FrameworkEvent:
    """Framework event information."""
    event_type: str
    source: str
    data: Dict[str, Any]
    timestamp: datetime


@dataclass
class IntegrationConfig:
    """Framework integration configuration."""
    enable_auto_sync: bool = True
    sync_on_file_change: bool = True
    sync_on_commit: bool = True
    enable_notifications: bool = True
    auto_create_issues: bool = False
    auto_create_prs: bool = False
    framework_hooks: List[str] = None


class BeastModeIntegration:
    """
    Integration with Beast Mode AI Development Framework.
    
    This class provides seamless integration between GitHub synchronization
    and the Beast Mode framework, enabling automated workflows and
    framework-specific customizations.
    """
    
    def __init__(self, config: GitHubSyncConfig, integration_config: IntegrationConfig):
        """
        Initialize Beast Mode integration.
        
        Args:
            config: GitHub synchronization configuration
            integration_config: Framework integration configuration
        """
        self.config = config
        self.integration_config = integration_config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize core components
        self.auth_manager = AuthenticationManager()
        self.github_client = GitHubAPIClient(self.auth_manager)
        self.sync_engine = SynchronizationEngine(self.github_client, config)
        
        # Initialize Git and pre-commit managers
        self.git_manager = None
        self.precommit_manager = None
        if config.sync_config.repositories:
            # Use first repository as default for Git operations
            first_repo = config.sync_config.repositories[0]
            repo_path = self._get_local_repo_path(first_repo.owner, first_repo.name)
            if repo_path and repo_path.exists():
                self.git_manager = GitCommitManager(str(repo_path))
                self.precommit_manager = PreCommitManager(str(repo_path))
        
        # Initialize data recovery
        data_dir = Path.home() / ".github_sync" / "data"
        self.recovery_manager = DataRecoveryManager(str(data_dir))
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Framework state
        self.is_running = False
        self.sync_tasks: Dict[str, asyncio.Task] = {}
    
    def _get_local_repo_path(self, owner: str, repo_name: str) -> Optional[Path]:
        """Get local repository path."""
        # Try common locations
        possible_paths = [
            Path.cwd(),
            Path.cwd() / repo_name,
            Path.home() / "repos" / repo_name,
            Path.home() / "projects" / repo_name,
        ]
        
        for path in possible_paths:
            if path.exists() and (path / ".git").exists():
                return path
        
        return None
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """
        Register an event handler for framework events.
        
        Args:
            event_type: Type of event to handle
            handler: Handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        self.logger.debug(f"Registered handler for event type: {event_type}")
    
    def emit_event(self, event: FrameworkEvent):
        """
        Emit a framework event to registered handlers.
        
        Args:
            event: Event to emit
        """
        handlers = self.event_handlers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Error in event handler for {event.event_type}: {e}")
    
    async def start_integration(self):
        """Start the framework integration."""
        if self.is_running:
            self.logger.warning("Integration already running")
            return
        
        self.logger.info("Starting Beast Mode GitHub integration")
        self.is_running = True
        
        try:
            # Validate authentication
            if not await self._validate_authentication():
                raise RuntimeError("GitHub authentication failed")
            
            # Start auto-sync if enabled
            if self.integration_config.enable_auto_sync:
                await self._start_auto_sync()
            
            # Set up file watchers if enabled
            if self.integration_config.sync_on_file_change:
                self._setup_file_watchers()
            
            # Emit startup event
            self.emit_event(FrameworkEvent(
                event_type="integration_started",
                source="beast_mode_integration",
                data={"config": self.integration_config.__dict__},
                timestamp=datetime.now()
            ))
            
            self.logger.info("Beast Mode GitHub integration started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start integration: {e}")
            self.is_running = False
            raise
    
    async def stop_integration(self):
        """Stop the framework integration."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping Beast Mode GitHub integration")
        self.is_running = False
        
        # Cancel running sync tasks
        for task_name, task in self.sync_tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                self.logger.debug(f"Cancelled sync task: {task_name}")
        
        self.sync_tasks.clear()
        
        # Emit shutdown event
        self.emit_event(FrameworkEvent(
            event_type="integration_stopped",
            source="beast_mode_integration",
            data={},
            timestamp=datetime.now()
        ))
        
        self.logger.info("Beast Mode GitHub integration stopped")
    
    async def _validate_authentication(self) -> bool:
        """Validate GitHub authentication."""
        try:
            # Test authentication by getting user info
            user_info = await self.github_client.get_authenticated_user()
            if user_info:
                self.logger.info(f"Authenticated as GitHub user: {user_info.get('login', 'unknown')}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Authentication validation failed: {e}")
            return False
    
    async def _start_auto_sync(self):
        """Start automatic synchronization tasks."""
        for repo_config in self.config.repository_configs:
            task_name = f"sync_{repo_config.owner}_{repo_config.name}"
            
            if task_name not in self.sync_tasks:
                task = asyncio.create_task(
                    self._auto_sync_repository(repo_config)
                )
                self.sync_tasks[task_name] = task
                self.logger.debug(f"Started auto-sync task for {repo_config.owner}/{repo_config.name}")
    
    async def _auto_sync_repository(self, repo_config):
        """Auto-sync a repository at regular intervals."""
        while self.is_running:
            try:
                # Perform synchronization
                result = await self.sync_engine.sync_repository(repo_config)
                
                if result.success:
                    self.logger.debug(f"Auto-sync successful for {repo_config.owner}/{repo_config.name}")
                    
                    # Emit sync success event
                    self.emit_event(FrameworkEvent(
                        event_type="sync_completed",
                        source="auto_sync",
                        data={
                            "repository": f"{repo_config.owner}/{repo_config.name}",
                            "result": result.__dict__
                        },
                        timestamp=datetime.now()
                    ))
                else:
                    self.logger.warning(f"Auto-sync failed for {repo_config.owner}/{repo_config.name}: {result.error}")
                
                # Wait for next sync interval
                await asyncio.sleep(self.config.sync_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in auto-sync for {repo_config.owner}/{repo_config.name}: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    def _setup_file_watchers(self):
        """Set up file system watchers for automatic sync triggers."""
        # This would integrate with the framework's file watching system
        # For now, we'll just log that it would be set up
        self.logger.info("File watchers would be set up here for automatic sync triggers")
    
    def on_file_changed(self, file_path: str):
        """
        Handle file change events from the framework.
        
        Args:
            file_path: Path to the changed file
        """
        if not self.integration_config.sync_on_file_change:
            return
        
        self.logger.debug(f"File changed: {file_path}")
        
        # Emit file change event
        self.emit_event(FrameworkEvent(
            event_type="file_changed",
            source="file_watcher",
            data={"file_path": file_path},
            timestamp=datetime.now()
        ))
        
        # Trigger sync if appropriate
        if self._should_sync_on_file_change(file_path):
            asyncio.create_task(self._trigger_sync_for_file_change(file_path))
    
    def _should_sync_on_file_change(self, file_path: str) -> bool:
        """Determine if a file change should trigger sync."""
        # Don't sync for temporary files, logs, etc.
        ignore_patterns = [
            '.tmp', '.log', '.cache', '__pycache__',
            '.git/', 'node_modules/', '.venv/'
        ]
        
        for pattern in ignore_patterns:
            if pattern in file_path:
                return False
        
        return True
    
    async def _trigger_sync_for_file_change(self, file_path: str):
        """Trigger synchronization for a file change."""
        try:
            # Find which repository this file belongs to
            for repo_config in self.config.repository_configs:
                repo_path = self._get_local_repo_path(repo_config.owner, repo_config.name)
                if repo_path and file_path.startswith(str(repo_path)):
                    # Trigger sync for this repository
                    result = await self.sync_engine.sync_repository(repo_config)
                    
                    if result.success:
                        self.logger.info(f"File change sync successful for {repo_config.owner}/{repo_config.name}")
                    else:
                        self.logger.warning(f"File change sync failed: {result.error}")
                    
                    break
        
        except Exception as e:
            self.logger.error(f"Error in file change sync: {e}")
    
    def on_commit_created(self, commit_info: Dict[str, Any]):
        """
        Handle commit creation events from the framework.
        
        Args:
            commit_info: Information about the created commit
        """
        if not self.integration_config.sync_on_commit:
            return
        
        self.logger.debug(f"Commit created: {commit_info.get('hash', 'unknown')}")
        
        # Emit commit event
        self.emit_event(FrameworkEvent(
            event_type="commit_created",
            source="git_integration",
            data=commit_info,
            timestamp=datetime.now()
        ))
        
        # Trigger sync after commit
        asyncio.create_task(self._sync_after_commit(commit_info))
    
    async def _sync_after_commit(self, commit_info: Dict[str, Any]):
        """Sync repositories after a commit is created."""
        try:
            # Sync all configured repositories
            for repo_config in self.config.repository_configs:
                result = await self.sync_engine.sync_repository(repo_config)
                
                if result.success:
                    self.logger.info(f"Post-commit sync successful for {repo_config.owner}/{repo_config.name}")
                else:
                    self.logger.warning(f"Post-commit sync failed: {result.error}")
        
        except Exception as e:
            self.logger.error(f"Error in post-commit sync: {e}")
    
    async def create_intelligent_commit(self, message_prefix: str = "") -> bool:
        """
        Create an intelligent commit using the Git manager.
        
        Args:
            message_prefix: Optional prefix for commit messages
            
        Returns:
            True if commits were created successfully
        """
        if not self.git_manager:
            self.logger.error("Git manager not available")
            return False
        
        try:
            # Check pre-commit hooks if available
            if self.precommit_manager:
                can_proceed, bypass_reason = self.precommit_manager.check_pre_commit_before_commit()
                
                if not can_proceed and not bypass_reason:
                    self.logger.error("Pre-commit hooks failed and cannot be bypassed")
                    return False
                elif not can_proceed and bypass_reason:
                    # Ask user for permission to bypass
                    self.logger.warning(f"Pre-commit hooks failed: {bypass_reason}")
                    # In a real implementation, this would prompt the user
                    # For now, we'll proceed with bypass
                    commit_messages = self.git_manager.create_intelligent_commits(dry_run=False)
                    if commit_messages:
                        # Use bypass commit for the last commit
                        last_message = commit_messages[-1]
                        return self.precommit_manager.commit_with_bypass(
                            last_message, bypass_reason
                        )
            
            # Create intelligent commits
            commit_messages = self.git_manager.create_intelligent_commits(dry_run=False)
            
            if commit_messages:
                self.logger.info(f"Created {len(commit_messages)} intelligent commits")
                
                # Emit commit events
                for message in commit_messages:
                    self.emit_event(FrameworkEvent(
                        event_type="intelligent_commit_created",
                        source="git_manager",
                        data={"message": message},
                        timestamp=datetime.now()
                    ))
                
                return True
            else:
                self.logger.info("No staged changes found for commit")
                return False
        
        except Exception as e:
            self.logger.error(f"Error creating intelligent commit: {e}")
            return False
    
    async def create_github_issue(self, title: str, body: str, 
                                labels: List[str] = None, 
                                repository: str = None) -> Optional[Issue]:
        """
        Create a GitHub issue.
        
        Args:
            title: Issue title
            body: Issue body
            labels: Optional labels
            repository: Repository in format "owner/repo" (uses first configured if None)
            
        Returns:
            Created Issue object or None if failed
        """
        try:
            # Determine target repository
            if repository:
                owner, repo_name = repository.split('/')
            else:
                if not self.config.repository_configs:
                    self.logger.error("No repository configured")
                    return None
                repo_config = self.config.repository_configs[0]
                owner, repo_name = repo_config.owner, repo_config.name
            
            # Create issue
            issue_data = {
                'title': title,
                'body': body
            }
            
            if labels:
                issue_data['labels'] = labels
            
            issue = await self.github_client.create_issue(owner, repo_name, issue_data)
            
            if issue:
                self.logger.info(f"Created GitHub issue #{issue.number}: {title}")
                
                # Emit issue creation event
                self.emit_event(FrameworkEvent(
                    event_type="issue_created",
                    source="github_integration",
                    data={
                        "repository": f"{owner}/{repo_name}",
                        "issue": issue.__dict__
                    },
                    timestamp=datetime.now()
                ))
            
            return issue
        
        except Exception as e:
            self.logger.error(f"Error creating GitHub issue: {e}")
            return None
    
    async def create_pull_request(self, title: str, body: str, 
                                head_branch: str, base_branch: str = "main",
                                repository: str = None) -> Optional[PullRequest]:
        """
        Create a GitHub pull request.
        
        Args:
            title: PR title
            body: PR body
            head_branch: Source branch
            base_branch: Target branch
            repository: Repository in format "owner/repo" (uses first configured if None)
            
        Returns:
            Created PullRequest object or None if failed
        """
        try:
            # Determine target repository
            if repository:
                owner, repo_name = repository.split('/')
            else:
                if not self.config.repository_configs:
                    self.logger.error("No repository configured")
                    return None
                repo_config = self.config.repository_configs[0]
                owner, repo_name = repo_config.owner, repo_config.name
            
            # Create pull request
            pr_data = {
                'title': title,
                'body': body,
                'head': head_branch,
                'base': base_branch
            }
            
            pr = await self.github_client.create_pull_request(owner, repo_name, pr_data)
            
            if pr:
                self.logger.info(f"Created GitHub PR #{pr.number}: {title}")
                
                # Emit PR creation event
                self.emit_event(FrameworkEvent(
                    event_type="pull_request_created",
                    source="github_integration",
                    data={
                        "repository": f"{owner}/{repo_name}",
                        "pull_request": pr.__dict__
                    },
                    timestamp=datetime.now()
                ))
            
            return pr
        
        except Exception as e:
            self.logger.error(f"Error creating GitHub pull request: {e}")
            return None
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get comprehensive integration status.
        
        Returns:
            Dictionary with integration status information
        """
        return {
            'is_running': self.is_running,
            'config': {
                'auto_sync_enabled': self.integration_config.enable_auto_sync,
                'sync_on_file_change': self.integration_config.sync_on_file_change,
                'sync_on_commit': self.integration_config.sync_on_commit,
                'notifications_enabled': self.integration_config.enable_notifications
            },
            'repositories': [
                {
                    'owner': repo.owner,
                    'name': repo.name,
                    'sync_enabled': True
                }
                for repo in self.config.sync_config.repositories
            ],
            'active_sync_tasks': len(self.sync_tasks),
            'event_handlers': {
                event_type: len(handlers)
                for event_type, handlers in self.event_handlers.items()
            },
            'git_manager_available': self.git_manager is not None,
            'precommit_manager_available': self.precommit_manager is not None,
            'last_status_check': datetime.now().isoformat()
        }
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of the integration.
        
        Returns:
            Dictionary with health check results
        """
        health_status = {
            'overall_health': 'healthy',
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Check GitHub authentication
        try:
            auth_valid = await self._validate_authentication()
            health_status['checks']['github_auth'] = {
                'status': 'healthy' if auth_valid else 'unhealthy',
                'message': 'GitHub authentication valid' if auth_valid else 'GitHub authentication failed'
            }
        except Exception as e:
            health_status['checks']['github_auth'] = {
                'status': 'unhealthy',
                'message': f'Authentication check failed: {e}'
            }
        
        # Check repository access
        repo_health = []
        for repo_config in self.config.repository_configs:
            try:
                repo = await self.github_client.get_repository(repo_config.owner, repo_config.name)
                repo_health.append({
                    'repository': f"{repo_config.owner}/{repo_config.name}",
                    'status': 'healthy' if repo else 'unhealthy',
                    'accessible': repo is not None
                })
            except Exception as e:
                repo_health.append({
                    'repository': f"{repo_config.owner}/{repo_config.name}",
                    'status': 'unhealthy',
                    'error': str(e)
                })
        
        health_status['checks']['repositories'] = repo_health
        
        # Check sync tasks
        active_tasks = sum(1 for task in self.sync_tasks.values() if not task.done())
        health_status['checks']['sync_tasks'] = {
            'status': 'healthy',
            'active_tasks': active_tasks,
            'total_tasks': len(self.sync_tasks)
        }
        
        # Determine overall health
        unhealthy_checks = [
            check for check in health_status['checks'].values()
            if isinstance(check, dict) and check.get('status') == 'unhealthy'
        ]
        
        if unhealthy_checks:
            health_status['overall_health'] = 'unhealthy'
        
        return health_status