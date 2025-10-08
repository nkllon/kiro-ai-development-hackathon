"""
Workflow customization and role-based access control for GitHub synchronization.

This module provides advanced workflow customization features including
role-based access control, custom event handlers, and selective synchronization.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum

from .models import Repository, Issue, PullRequest, Commit

logger = logging.getLogger(__name__)


class Permission(Enum):
    """Available permissions for GitHub sync operations."""
    READ_REPOSITORIES = "read_repositories"
    WRITE_REPOSITORIES = "write_repositories"
    MANAGE_SYNC = "manage_sync"
    MANAGE_WEBHOOKS = "manage_webhooks"
    MANAGE_CONFIG = "manage_config"
    VIEW_METRICS = "view_metrics"
    MANAGE_USERS = "manage_users"
    ADMIN = "admin"


class EventType(Enum):
    """Types of synchronization events."""
    SYNC_STARTED = "sync_started"
    SYNC_COMPLETED = "sync_completed"
    SYNC_FAILED = "sync_failed"
    REPOSITORY_ADDED = "repository_added"
    REPOSITORY_REMOVED = "repository_removed"
    ISSUE_SYNCED = "issue_synced"
    PR_SYNCED = "pr_synced"
    COMMIT_SYNCED = "commit_synced"
    WEBHOOK_RECEIVED = "webhook_received"
    RATE_LIMIT_HIT = "rate_limit_hit"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class Role:
    """User role with associated permissions."""
    name: str
    permissions: Set[Permission]
    description: Optional[str] = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if role has a specific permission."""
        return permission in self.permissions or Permission.ADMIN in self.permissions
    
    def can_access_repository(self, repository: str, permission: Permission) -> bool:
        """Check if role can access a specific repository with given permission."""
        # Admin can access everything
        if Permission.ADMIN in self.permissions:
            return True
        
        # Check specific permission
        return self.has_permission(permission)


@dataclass
class User:
    """User with role-based permissions."""
    username: str
    roles: List[Role]
    github_username: Optional[str] = None
    email: Optional[str] = None
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission through any role."""
        if not self.active:
            return False
        
        return any(role.has_permission(permission) for role in self.roles)
    
    def can_access_repository(self, repository: str, permission: Permission) -> bool:
        """Check if user can access a specific repository with given permission."""
        if not self.active:
            return False
        
        return any(role.can_access_repository(repository, permission) for role in self.roles)
    
    def get_permissions(self) -> Set[Permission]:
        """Get all permissions for this user."""
        permissions = set()
        for role in self.roles:
            permissions.update(role.permissions)
        return permissions


@dataclass
class SyncEvent:
    """Represents a synchronization event."""
    event_type: EventType
    timestamp: datetime
    repository: Optional[str] = None
    user: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'repository': self.repository,
            'user': self.user,
            'data': self.data,
            'success': self.success,
            'error_message': self.error_message
        }


class EventHandler(ABC):
    """Abstract base class for custom event handlers."""
    
    @abstractmethod
    def handle_event(self, event: SyncEvent) -> None:
        """Handle a synchronization event."""
        pass
    
    @abstractmethod
    def get_supported_events(self) -> List[EventType]:
        """Get list of event types this handler supports."""
        pass


class LoggingEventHandler(EventHandler):
    """Event handler that logs events."""
    
    def __init__(self, log_level: str = "INFO"):
        """Initialize logging event handler."""
        self.logger = logging.getLogger(f"{__name__}.events")
        self.log_level = getattr(logging, log_level.upper())
    
    def handle_event(self, event: SyncEvent) -> None:
        """Log the event."""
        message = f"GitHub Sync Event: {event.event_type.value}"
        if event.repository:
            message += f" for {event.repository}"
        if event.user:
            message += f" by {event.user}"
        
        if event.success:
            self.logger.log(self.log_level, message)
        else:
            self.logger.error(f"{message} - Error: {event.error_message}")
    
    def get_supported_events(self) -> List[EventType]:
        """Support all event types."""
        return list(EventType)


class MetricsEventHandler(EventHandler):
    """Event handler that collects metrics."""
    
    def __init__(self):
        """Initialize metrics event handler."""
        self.metrics: Dict[str, Any] = {
            'sync_count': 0,
            'sync_success_count': 0,
            'sync_failure_count': 0,
            'repository_count': 0,
            'last_sync': None,
            'events_by_type': {},
            'events_by_repository': {}
        }
    
    def handle_event(self, event: SyncEvent) -> None:
        """Update metrics based on event."""
        # Update event type counters
        event_type_key = event.event_type.value
        self.metrics['events_by_type'][event_type_key] = \
            self.metrics['events_by_type'].get(event_type_key, 0) + 1
        
        # Update repository counters
        if event.repository:
            self.metrics['events_by_repository'][event.repository] = \
                self.metrics['events_by_repository'].get(event.repository, 0) + 1
        
        # Update sync-specific metrics
        if event.event_type == EventType.SYNC_COMPLETED:
            self.metrics['sync_count'] += 1
            if event.success:
                self.metrics['sync_success_count'] += 1
            else:
                self.metrics['sync_failure_count'] += 1
            self.metrics['last_sync'] = event.timestamp.isoformat()
        
        elif event.event_type == EventType.REPOSITORY_ADDED:
            self.metrics['repository_count'] += 1
        
        elif event.event_type == EventType.REPOSITORY_REMOVED:
            self.metrics['repository_count'] = max(0, self.metrics['repository_count'] - 1)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    def get_supported_events(self) -> List[EventType]:
        """Support all event types."""
        return list(EventType)


class CustomSyncRule:
    """Custom synchronization rule."""
    
    def __init__(self, name: str, condition: Callable[[Dict[str, Any]], bool], 
                 action: Callable[[Dict[str, Any]], None]):
        """
        Initialize custom sync rule.
        
        Args:
            name: Rule name
            condition: Function that returns True if rule should apply
            action: Function to execute when rule applies
        """
        self.name = name
        self.condition = condition
        self.action = action
        self.enabled = True
        self.execution_count = 0
        self.last_executed = None
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate if this rule should be applied."""
        if not self.enabled:
            return False
        
        try:
            return self.condition(context)
        except Exception as e:
            logger.error(f"Error evaluating rule {self.name}: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> None:
        """Execute the rule action."""
        try:
            self.action(context)
            self.execution_count += 1
            self.last_executed = datetime.utcnow()
        except Exception as e:
            logger.error(f"Error executing rule {self.name}: {e}")
            raise


class WorkflowManager:
    """
    Manages workflow customization and role-based access control.
    
    This class provides comprehensive workflow management including
    user roles, permissions, event handling, and custom sync rules.
    """
    
    def __init__(self):
        """Initialize workflow manager."""
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.event_handlers: List[EventHandler] = []
        self.custom_rules: List[CustomSyncRule] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize default roles
        self._create_default_roles()
        
        # Add default event handlers
        self.add_event_handler(LoggingEventHandler())
        self.add_event_handler(MetricsEventHandler())
    
    def _create_default_roles(self) -> None:
        """Create default user roles."""
        # Admin role with all permissions
        admin_role = Role(
            name="admin",
            permissions={Permission.ADMIN},
            description="Full administrative access"
        )
        self.roles["admin"] = admin_role
        
        # Manager role with most permissions
        manager_role = Role(
            name="manager",
            permissions={
                Permission.READ_REPOSITORIES,
                Permission.WRITE_REPOSITORIES,
                Permission.MANAGE_SYNC,
                Permission.MANAGE_WEBHOOKS,
                Permission.MANAGE_CONFIG,
                Permission.VIEW_METRICS
            },
            description="Management access to sync operations"
        )
        self.roles["manager"] = manager_role
        
        # Developer role with read/write access
        developer_role = Role(
            name="developer",
            permissions={
                Permission.READ_REPOSITORIES,
                Permission.WRITE_REPOSITORIES,
                Permission.VIEW_METRICS
            },
            description="Developer access to repositories"
        )
        self.roles["developer"] = developer_role
        
        # Viewer role with read-only access
        viewer_role = Role(
            name="viewer",
            permissions={
                Permission.READ_REPOSITORIES,
                Permission.VIEW_METRICS
            },
            description="Read-only access to repositories and metrics"
        )
        self.roles["viewer"] = viewer_role
    
    def create_role(self, name: str, permissions: Set[Permission], 
                   description: Optional[str] = None) -> Role:
        """
        Create a new role.
        
        Args:
            name: Role name
            permissions: Set of permissions
            description: Optional description
            
        Returns:
            Created role
        """
        role = Role(name=name, permissions=permissions, description=description)
        self.roles[name] = role
        return role
    
    def create_user(self, username: str, role_names: List[str], 
                   github_username: Optional[str] = None, 
                   email: Optional[str] = None) -> User:
        """
        Create a new user.
        
        Args:
            username: Username
            role_names: List of role names to assign
            github_username: Optional GitHub username
            email: Optional email address
            
        Returns:
            Created user
        """
        roles = []
        for role_name in role_names:
            if role_name in self.roles:
                roles.append(self.roles[role_name])
            else:
                raise ValueError(f"Role '{role_name}' does not exist")
        
        user = User(
            username=username,
            roles=roles,
            github_username=github_username,
            email=email
        )
        self.users[username] = user
        return user
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.users.get(username)
    
    def check_permission(self, username: str, permission: Permission, 
                        repository: Optional[str] = None) -> bool:
        """
        Check if user has permission for an operation.
        
        Args:
            username: Username
            permission: Required permission
            repository: Optional repository name for repository-specific permissions
            
        Returns:
            True if user has permission
        """
        user = self.get_user(username)
        if not user:
            return False
        
        if repository:
            return user.can_access_repository(repository, permission)
        else:
            return user.has_permission(permission)
    
    def require_permission(self, username: str, permission: Permission, 
                          repository: Optional[str] = None) -> None:
        """
        Require user to have permission, raise exception if not.
        
        Args:
            username: Username
            permission: Required permission
            repository: Optional repository name
            
        Raises:
            PermissionError: If user doesn't have required permission
        """
        if not self.check_permission(username, permission, repository):
            repo_text = f" for repository {repository}" if repository else ""
            raise PermissionError(
                f"User {username} does not have {permission.value} permission{repo_text}"
            )
    
    def add_event_handler(self, handler: EventHandler) -> None:
        """Add an event handler."""
        self.event_handlers.append(handler)
    
    def remove_event_handler(self, handler: EventHandler) -> None:
        """Remove an event handler."""
        if handler in self.event_handlers:
            self.event_handlers.remove(handler)
    
    def emit_event(self, event: SyncEvent) -> None:
        """
        Emit an event to all registered handlers.
        
        Args:
            event: Event to emit
        """
        for handler in self.event_handlers:
            try:
                if event.event_type in handler.get_supported_events():
                    handler.handle_event(event)
            except Exception as e:
                self.logger.error(f"Event handler {handler.__class__.__name__} failed: {e}")
    
    def add_custom_rule(self, rule: CustomSyncRule) -> None:
        """Add a custom synchronization rule."""
        self.custom_rules.append(rule)
    
    def remove_custom_rule(self, rule_name: str) -> bool:
        """Remove a custom synchronization rule by name."""
        for i, rule in enumerate(self.custom_rules):
            if rule.name == rule_name:
                del self.custom_rules[i]
                return True
        return False
    
    def apply_custom_rules(self, context: Dict[str, Any]) -> None:
        """
        Apply all enabled custom rules to the given context.
        
        Args:
            context: Context data for rule evaluation
        """
        for rule in self.custom_rules:
            if rule.evaluate(context):
                try:
                    rule.execute(context)
                    self.logger.debug(f"Applied custom rule: {rule.name}")
                except Exception as e:
                    self.logger.error(f"Failed to apply custom rule {rule.name}: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics from metrics event handler."""
        for handler in self.event_handlers:
            if isinstance(handler, MetricsEventHandler):
                return handler.get_metrics()
        return {}
    
    def create_sync_context(self, repository: str, user: str, 
                           operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create context for synchronization operations.
        
        Args:
            repository: Repository name
            user: Username
            operation: Operation being performed
            data: Additional context data
            
        Returns:
            Context dictionary
        """
        return {
            'repository': repository,
            'user': user,
            'operation': operation,
            'timestamp': datetime.utcnow(),
            'data': data
        }


# Predefined custom rule factories
def create_priority_sync_rule(high_priority_repos: List[str]) -> CustomSyncRule:
    """Create a rule that prioritizes certain repositories for syncing."""
    def condition(context: Dict[str, Any]) -> bool:
        return context.get('repository') in high_priority_repos
    
    def action(context: Dict[str, Any]) -> None:
        # Increase sync priority
        context['priority'] = context.get('priority', 1) + 10
    
    return CustomSyncRule(
        name="priority_sync",
        condition=condition,
        action=action
    )


def create_business_hours_rule(start_hour: int = 9, end_hour: int = 17) -> CustomSyncRule:
    """Create a rule that only allows syncing during business hours."""
    def condition(context: Dict[str, Any]) -> bool:
        current_hour = datetime.now().hour
        return not (start_hour <= current_hour <= end_hour)
    
    def action(context: Dict[str, Any]) -> None:
        # Delay sync until business hours
        context['delay_until_business_hours'] = True
    
    return CustomSyncRule(
        name="business_hours_only",
        condition=condition,
        action=action
    )


def create_error_threshold_rule(max_errors: int = 5) -> CustomSyncRule:
    """Create a rule that disables sync after too many errors."""
    error_counts = {}
    
    def condition(context: Dict[str, Any]) -> bool:
        repo = context.get('repository')
        if not repo:
            return False
        
        error_count = error_counts.get(repo, 0)
        if context.get('error_occurred'):
            error_counts[repo] = error_count + 1
        
        return error_counts.get(repo, 0) >= max_errors
    
    def action(context: Dict[str, Any]) -> None:
        # Disable sync for this repository
        context['disable_sync'] = True
        context['disable_reason'] = f"Too many errors (>{max_errors})"
    
    return CustomSyncRule(
        name="error_threshold",
        condition=condition,
        action=action
    )