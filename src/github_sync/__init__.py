"""
GitHub Synchronization Module

This module provides comprehensive GitHub integration for the Beast Mode AI Development Framework.
It enables bidirectional synchronization of repository data, issues, pull requests, and 
collaborative features while maintaining security best practices.
"""

from .models import Repository, Issue, PullRequest, Commit
from .config import GitHubConfig, RepositoryConfig, SyncConfig
from .config_manager import ConfigurationManager, AdvancedRepositoryConfig, AdvancedSyncConfig, ContentFilter, SyncSchedule
from .auth import AuthenticationManager
from .client import GitHubAPIClient
from .sync import SynchronizationEngine
from .cache import CacheManager
from .webhooks import WebhookHandler
from .reviews import CodeReviewIntegration, Review, ReviewComment, ReviewSummary
from .projects import ProjectManagementIntegration, Project, ProjectColumn, ProjectCard, Milestone, Notification
from .workflows import WorkflowManager, Role, User, Permission, EventHandler, CustomSyncRule, SyncEvent
from .monitoring import MetricsCollector, StructuredLogger, PerformanceMonitor, SyncMetrics, APIMetrics, SystemMetrics
from .health import HealthMonitor, SystemHealth, HealthCheck, HealthStatus
from .error_recovery import ErrorRecoveryManager, ErrorCategory, RecoveryStrategy, ErrorContext, RecoveryAction

__version__ = "1.0.0"
__all__ = [
    "Repository",
    "Issue", 
    "PullRequest",
    "Commit",
    "GitHubConfig",
    "RepositoryConfig", 
    "SyncConfig",
    "ConfigurationManager",
    "AdvancedRepositoryConfig",
    "AdvancedSyncConfig",
    "ContentFilter",
    "SyncSchedule",
    "AuthenticationManager",
    "GitHubAPIClient",
    "SynchronizationEngine",
    "CacheManager",
    "WebhookHandler",
    "CodeReviewIntegration",
    "Review",
    "ReviewComment", 
    "ReviewSummary",
    "ProjectManagementIntegration",
    "Project",
    "ProjectColumn",
    "ProjectCard",
    "Milestone",
    "Notification",
    "WorkflowManager",
    "Role",
    "User",
    "Permission",
    "EventHandler",
    "CustomSyncRule",
    "SyncEvent",
    "MetricsCollector",
    "StructuredLogger",
    "PerformanceMonitor",
    "SyncMetrics",
    "APIMetrics",
    "SystemMetrics",
    "HealthMonitor",
    "SystemHealth",
    "HealthCheck",
    "HealthStatus",
    "ErrorRecoveryManager",
    "ErrorCategory",
    "RecoveryStrategy",
    "ErrorContext",
    "RecoveryAction",
]