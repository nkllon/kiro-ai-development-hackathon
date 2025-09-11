#!/usr/bin/env python3
"""
Multi-Project Models - Multi-project management data classes

Extracted from models.py for RM-DDD compliance.
Single responsibility: Multi-project management data classes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from .core_models import (
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime

    ConflictResolutionStrategy, CompletionStatus, NotificationSettings,
    DevpostConfig, Deadline
)


@dataclass
class ProjectConnection(ReflectiveModule):
    """Local project to Devpost connection mapping."""
    local_project_id: str
    devpost_project_id: str
    connection_type: str = "primary"  # 'primary', 'backup', 'mirror'
    created_at: datetime = field(default_factory=datetime.now)
    last_synced: Optional[datetime] = None
    sync_status: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiProjectConfig:
    """Multi-project management configuration."""
    max_concurrent_projects: int = 5
    default_timeout: int = 300
    auto_save_interval: int = 60
    conflict_resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MANUAL
    project_isolation: bool = True
    shared_resources: List[str] = field(default_factory=list)
    project_connections: List[ProjectConnection] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ContextSwitchResult:
    """Multi-project context switch result."""
    success: bool
    from_project_id: Optional[str] = None
    to_project_id: Optional[str] = None
    switch_time: datetime = field(default_factory=datetime.now)
    context_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConflictResolution:
    """Multi-project conflict resolution result."""
    conflict_id: str
    project_ids: List[str]
    conflict_type: str
    resolution_strategy: ConflictResolutionStrategy
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    resolution_details: Optional[str] = None
    auto_resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectDashboard:
    """Multi-project dashboard data."""
    total_projects: int
    active_projects: int
    completed_projects: int
    projects: List[Dict[str, Any]] = field(default_factory=list)
    recent_activity: List[Dict[str, Any]] = field(default_factory=list)
    upcoming_deadlines: List[Deadline] = field(default_factory=list)
    system_status: str = "healthy"
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationMessage:
    """Notification message data."""
    message_id: str
    title: str
    message: str
    notification_type: str
    priority: str = "normal"  # 'low', 'normal', 'high', 'urgent'
    created_at: datetime = field(default_factory=datetime.now)
    read: bool = False
    project_id: Optional[str] = None
    action_required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReminderTiming:
    """Deadline reminder timing configuration."""
    reminder_id: str
    deadline_id: str
    reminder_times: List[datetime] = field(default_factory=list)
    notification_type: str = "email"
    enabled: bool = True
    custom_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Multi Project Models',
            'description': 'multi_project_models module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return []
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
            # Add module-specific health checks here
            
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {self.module_id} module")


@dataclass
class GlobalSettings:
    """Global settings for multi-project management."""
    theme: str = "default"
    language: str = "en"
    timezone: str = "UTC"
    auto_sync: bool = True
    debug_mode: bool = False
    log_level: str = "INFO"
    max_log_files: int = 10
    backup_enabled: bool = True
    backup_interval: int = 24  # hours
    metadata: Dict[str, Any] = field(default_factory=dict)
