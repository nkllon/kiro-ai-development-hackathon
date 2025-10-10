"""
Advanced configuration management system for GitHub synchronization.

This module provides enhanced configuration management capabilities including
repository selection, filtering, sync schedules, and workflow customization.
"""

import os
import json
import logging
from datetime import datetime, time
from pathlib import Path
from typing import List, Optional, Dict, Any, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum

from .config import GitHubConfig, RepositoryConfig, SyncConfig, SyncStrategy, ConflictResolutionStrategy

logger = logging.getLogger(__name__)


class FilterType(Enum):
    """Types of content filters."""
    INCLUDE = "include"
    EXCLUDE = "exclude"


class ScheduleType(Enum):
    """Types of sync schedules."""
    INTERVAL = "interval"
    CRON = "cron"
    MANUAL = "manual"


@dataclass
class ContentFilter:
    """Filter for selective synchronization."""
    filter_type: FilterType
    content_type: str  # "issues", "pull_requests", "commits", "branches"
    criteria: Dict[str, Any]  # Filter criteria (labels, states, etc.)
    
    def matches(self, item: Dict[str, Any]) -> bool:
        """Check if an item matches this filter."""
        for key, expected_value in self.criteria.items():
            item_value = item.get(key)
            
            if isinstance(expected_value, list):
                # Check if item value is in the expected list
                if item_value not in expected_value:
                    return False
            elif isinstance(expected_value, str):
                # String matching (case-insensitive)
                if not item_value or expected_value.lower() not in str(item_value).lower():
                    return False
            else:
                # Exact match
                if item_value != expected_value:
                    return False
        
        return True


@dataclass
class SyncSchedule:
    """Synchronization schedule configuration."""
    schedule_type: ScheduleType
    interval_seconds: Optional[int] = None
    cron_expression: Optional[str] = None
    timezone: str = "UTC"
    enabled: bool = True
    next_run: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate schedule configuration."""
        if self.schedule_type == ScheduleType.INTERVAL and not self.interval_seconds:
            raise ValueError("Interval schedule requires interval_seconds")
        
        if self.schedule_type == ScheduleType.CRON and not self.cron_expression:
            raise ValueError("Cron schedule requires cron_expression")
        
        if isinstance(self.schedule_type, str):
            self.schedule_type = ScheduleType(self.schedule_type)


@dataclass
class AdvancedRepositoryConfig(RepositoryConfig):
    """Enhanced repository configuration with advanced features."""
    content_filters: List[ContentFilter] = field(default_factory=list)
    sync_schedule: Optional[SyncSchedule] = None
    priority: int = 1  # Higher numbers = higher priority
    tags: List[str] = field(default_factory=list)
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    last_sync: Optional[datetime] = None
    sync_errors: List[str] = field(default_factory=list)
    
    def add_filter(self, filter_type: FilterType, content_type: str, **criteria) -> None:
        """Add a content filter to this repository."""
        content_filter = ContentFilter(
            filter_type=filter_type,
            content_type=content_type,
            criteria=criteria
        )
        self.content_filters.append(content_filter)
    
    def should_sync_item(self, content_type: str, item: Dict[str, Any]) -> bool:
        """Check if an item should be synchronized based on filters."""
        relevant_filters = [f for f in self.content_filters if f.content_type == content_type]
        
        if not relevant_filters:
            return True  # No filters = sync everything
        
        # Apply include filters first
        include_filters = [f for f in relevant_filters if f.filter_type == FilterType.INCLUDE]
        if include_filters:
            # Must match at least one include filter
            if not any(f.matches(item) for f in include_filters):
                return False
        
        # Apply exclude filters
        exclude_filters = [f for f in relevant_filters if f.filter_type == FilterType.EXCLUDE]
        if exclude_filters:
            # Must not match any exclude filter
            if any(f.matches(item) for f in exclude_filters):
                return False
        
        return True
    
    def update_sync_status(self, success: bool, error_message: Optional[str] = None) -> None:
        """Update synchronization status."""
        self.last_sync = datetime.utcnow()
        
        if success:
            self.sync_errors.clear()
        elif error_message:
            self.sync_errors.append(f"{datetime.utcnow().isoformat()}: {error_message}")
            # Keep only last 10 errors
            self.sync_errors = self.sync_errors[-10:]


@dataclass
class AdvancedSyncConfig(SyncConfig):
    """Enhanced sync configuration with advanced scheduling and filtering."""
    global_filters: List[ContentFilter] = field(default_factory=list)
    default_schedule: Optional[SyncSchedule] = None
    repository_groups: Dict[str, List[str]] = field(default_factory=dict)  # group_name -> repo_full_names
    webhook_retry_attempts: int = 3
    webhook_retry_delay: int = 5  # seconds
    performance_monitoring: bool = True
    auto_cleanup_old_data: bool = True
    cleanup_retention_days: int = 90
    
    def add_repository_group(self, group_name: str, repositories: List[str]) -> None:
        """Add a group of repositories for batch operations."""
        self.repository_groups[group_name] = repositories
    
    def get_repositories_in_group(self, group_name: str) -> List[str]:
        """Get repository names in a group."""
        return self.repository_groups.get(group_name, [])
    
    def add_global_filter(self, filter_type: FilterType, content_type: str, **criteria) -> None:
        """Add a global filter that applies to all repositories."""
        global_filter = ContentFilter(
            filter_type=filter_type,
            content_type=content_type,
            criteria=criteria
        )
        self.global_filters.append(global_filter)


class ConfigurationManager:
    """
    Advanced configuration management system.
    
    This class provides comprehensive configuration management including
    repository selection, filtering, scheduling, and persistence.
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file or Path.home() / ".github_sync_config.json"
        self.config: Optional[GitHubConfig] = None
        self.logger = logging.getLogger(__name__)
        
        # Configuration change callbacks
        self.change_callbacks: List[Callable[[GitHubConfig], None]] = []
    
    def load_config(self) -> GitHubConfig:
        """
        Load configuration from file or create default.
        
        Returns:
            GitHubConfig instance
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                self.config = self._deserialize_config(config_data)
                self.logger.info(f"Loaded configuration from {self.config_file}")
                
            except Exception as e:
                self.logger.error(f"Failed to load config from {self.config_file}: {e}")
                self.config = GitHubConfig.from_env()
        else:
            self.config = GitHubConfig.from_env()
            self.save_config()  # Save default config
        
        return self.config
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        if not self.config:
            raise ValueError("No configuration to save")
        
        try:
            config_data = self._serialize_config(self.config)
            
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write configuration
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            self.logger.info(f"Saved configuration to {self.config_file}")
            
            # Notify callbacks
            for callback in self.change_callbacks:
                try:
                    callback(self.config)
                except Exception as e:
                    self.logger.error(f"Configuration change callback failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to save config to {self.config_file}: {e}")
            raise
    
    def add_repository(self, owner: str, name: str, **kwargs) -> AdvancedRepositoryConfig:
        """
        Add a repository to the configuration.
        
        Args:
            owner: Repository owner
            name: Repository name
            **kwargs: Additional repository configuration options
            
        Returns:
            Created repository configuration
        """
        if not self.config:
            self.load_config()
        
        # Create advanced repository config
        repo_config = AdvancedRepositoryConfig(owner=owner, name=name, **kwargs)
        
        # Convert sync_config to advanced if needed
        if not isinstance(self.config.sync_config, AdvancedSyncConfig):
            self.config.sync_config = self._upgrade_sync_config(self.config.sync_config)
        
        self.config.sync_config.repositories.append(repo_config)
        self.save_config()
        
        return repo_config
    
    def remove_repository(self, owner: str, name: str) -> bool:
        """
        Remove a repository from the configuration.
        
        Args:
            owner: Repository owner
            name: Repository name
            
        Returns:
            True if repository was removed
        """
        if not self.config:
            self.load_config()
        
        full_name = f"{owner}/{name}"
        for i, repo in enumerate(self.config.sync_config.repositories):
            if repo.full_name == full_name:
                del self.config.sync_config.repositories[i]
                self.save_config()
                return True
        
        return False
    
    def get_repository_config(self, owner: str, name: str) -> Optional[AdvancedRepositoryConfig]:
        """
        Get configuration for a specific repository.
        
        Args:
            owner: Repository owner
            name: Repository name
            
        Returns:
            Repository configuration or None if not found
        """
        if not self.config:
            self.load_config()
        
        full_name = f"{owner}/{name}"
        for repo in self.config.sync_config.repositories:
            if repo.full_name == full_name:
                return repo
        
        return None
    
    def list_repositories(self, tags: Optional[List[str]] = None, 
                         group: Optional[str] = None) -> List[AdvancedRepositoryConfig]:
        """
        List repositories with optional filtering.
        
        Args:
            tags: Filter by tags
            group: Filter by repository group
            
        Returns:
            List of matching repository configurations
        """
        if not self.config:
            self.load_config()
        
        repositories = self.config.sync_config.repositories
        
        # Filter by group
        if group and isinstance(self.config.sync_config, AdvancedSyncConfig):
            group_repos = set(self.config.sync_config.get_repositories_in_group(group))
            repositories = [r for r in repositories if r.full_name in group_repos]
        
        # Filter by tags
        if tags:
            repositories = [
                r for r in repositories 
                if isinstance(r, AdvancedRepositoryConfig) and 
                any(tag in r.tags for tag in tags)
            ]
        
        return repositories
    
    def add_content_filter(self, owner: str, name: str, filter_type: FilterType, 
                          content_type: str, **criteria) -> None:
        """
        Add a content filter to a repository.
        
        Args:
            owner: Repository owner
            name: Repository name
            filter_type: Include or exclude filter
            content_type: Type of content to filter
            **criteria: Filter criteria
        """
        repo_config = self.get_repository_config(owner, name)
        if not repo_config:
            raise ValueError(f"Repository {owner}/{name} not found in configuration")
        
        if not isinstance(repo_config, AdvancedRepositoryConfig):
            raise ValueError("Repository must be upgraded to advanced configuration")
        
        repo_config.add_filter(filter_type, content_type, **criteria)
        self.save_config()
    
    def set_sync_schedule(self, owner: str, name: str, schedule: SyncSchedule) -> None:
        """
        Set synchronization schedule for a repository.
        
        Args:
            owner: Repository owner
            name: Repository name
            schedule: Sync schedule configuration
        """
        repo_config = self.get_repository_config(owner, name)
        if not repo_config:
            raise ValueError(f"Repository {owner}/{name} not found in configuration")
        
        if not isinstance(repo_config, AdvancedRepositoryConfig):
            raise ValueError("Repository must be upgraded to advanced configuration")
        
        repo_config.sync_schedule = schedule
        self.save_config()
    
    def add_change_callback(self, callback: Callable[[GitHubConfig], None]) -> None:
        """Add a callback to be called when configuration changes."""
        self.change_callbacks.append(callback)
    
    def validate_configuration(self) -> List[str]:
        """
        Validate the current configuration.
        
        Returns:
            List of validation errors
        """
        if not self.config:
            self.load_config()
        
        errors = self.config.validate()
        
        # Additional validation for advanced features
        for repo in self.config.sync_config.repositories:
            if isinstance(repo, AdvancedRepositoryConfig):
                # Validate filters
                for content_filter in repo.content_filters:
                    if not content_filter.criteria:
                        errors.append(f"Empty filter criteria for {repo.full_name}")
                
                # Validate schedule
                if repo.sync_schedule:
                    try:
                        # Basic schedule validation
                        if repo.sync_schedule.schedule_type == ScheduleType.INTERVAL:
                            if repo.sync_schedule.interval_seconds < 60:
                                errors.append(f"Sync interval too short for {repo.full_name}")
                    except Exception as e:
                        errors.append(f"Invalid schedule for {repo.full_name}: {e}")
        
        return errors
    
    def _serialize_config(self, config: GitHubConfig) -> Dict[str, Any]:
        """Serialize configuration to dictionary."""
        # Note: We don't serialize credentials for security
        return {
            'api_base_url': config.api_base_url,
            'webhook_base_url': config.webhook_base_url,
            'user_agent': config.user_agent,
            'sync_config': self._serialize_sync_config(config.sync_config)
        }
    
    def _serialize_sync_config(self, sync_config: SyncConfig) -> Dict[str, Any]:
        """Serialize sync configuration to dictionary."""
        data = asdict(sync_config)
        
        # Handle enum serialization
        if 'conflict_resolution' in data:
            data['conflict_resolution'] = data['conflict_resolution'].value
        
        # Serialize repositories
        if 'repositories' in data:
            data['repositories'] = [self._serialize_repository(repo) for repo in sync_config.repositories]
        
        return data
    
    def _serialize_repository(self, repo: RepositoryConfig) -> Dict[str, Any]:
        """Serialize repository configuration to dictionary."""
        data = asdict(repo)
        
        # Handle enum serialization
        if 'sync_strategy' in data:
            data['sync_strategy'] = data['sync_strategy'].value
        
        return data
    
    def _deserialize_config(self, data: Dict[str, Any]) -> GitHubConfig:
        """Deserialize configuration from dictionary."""
        # Load credentials from environment (never from file)
        config = GitHubConfig.from_env()
        
        # Update with saved settings
        config.api_base_url = data.get('api_base_url', config.api_base_url)
        config.webhook_base_url = data.get('webhook_base_url', config.webhook_base_url)
        config.user_agent = data.get('user_agent', config.user_agent)
        
        # Deserialize sync config
        if 'sync_config' in data:
            config.sync_config = self._deserialize_sync_config(data['sync_config'])
        
        return config
    
    def _deserialize_sync_config(self, data: Dict[str, Any]) -> AdvancedSyncConfig:
        """Deserialize sync configuration from dictionary."""
        # Create advanced sync config
        sync_config = AdvancedSyncConfig()
        
        # Update with saved values
        for key, value in data.items():
            if key == 'conflict_resolution':
                sync_config.conflict_resolution = ConflictResolutionStrategy(value)
            elif key == 'repositories':
                sync_config.repositories = [self._deserialize_repository(repo_data) for repo_data in value]
            elif hasattr(sync_config, key):
                setattr(sync_config, key, value)
        
        return sync_config
    
    def _deserialize_repository(self, data: Dict[str, Any]) -> AdvancedRepositoryConfig:
        """Deserialize repository configuration from dictionary."""
        # Handle enum deserialization
        if 'sync_strategy' in data:
            data['sync_strategy'] = SyncStrategy(data['sync_strategy'])
        
        # Create advanced repository config
        repo_config = AdvancedRepositoryConfig(**data)
        
        return repo_config
    
    def _upgrade_sync_config(self, sync_config: SyncConfig) -> AdvancedSyncConfig:
        """Upgrade basic sync config to advanced sync config."""
        advanced_config = AdvancedSyncConfig()
        
        # Copy all basic attributes
        for key, value in asdict(sync_config).items():
            if hasattr(advanced_config, key):
                setattr(advanced_config, key, value)
        
        return advanced_config