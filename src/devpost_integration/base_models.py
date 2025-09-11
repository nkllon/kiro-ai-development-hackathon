#!/usr/bin/env python3
"""
Base Models - Base data classes and core models

Extracted from core_models.py for RM-DDD compliance.
Single responsibility: Base data classes and core model definitions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from .enums import (
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime

    MediaType, NotificationTiming, ValidationSeverity
)


@dataclass
class TeamMember(ReflectiveModule):
    """Team member information."""
    name: str
    email: Optional[str] = None
    role: Optional[str] = None
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None


@dataclass
class ProjectLink:
    """Project link information."""
    url: str
    link_type: str  # 'github', 'demo', 'documentation', 'video', 'other'
    title: Optional[str] = None
    description: Optional[str] = None


@dataclass
class MediaFile:
    """Media file information."""
    file_path: str
    media_type: MediaType
    file_size: int
    mime_type: Optional[str] = None
    dimensions: Optional[str] = None
    duration: Optional[float] = None
    file_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubmissionRequirement:
    """Hackathon submission requirement."""
    requirement_id: str
    title: str
    description: str
    required: bool = True
    file_types: List[str] = field(default_factory=list)
    max_size: Optional[int] = None
    deadline: Optional[datetime] = None


@dataclass
class SyncOperation:
    """Synchronization operation details."""
    operation_id: str
    operation_type: str  # Will be imported from enums
    file_path: str
    timestamp: datetime
    status: str = "pending"  # 'pending', 'in_progress', 'completed', 'failed'
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FileChangeEvent:
    """File system change event."""
    file_path: str
    change_type: str  # Will be imported from enums
    timestamp: datetime
    content_type: str  # Will be imported from enums
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Deadline:
    """Hackathon deadline information."""
    deadline_id: str
    title: str
    deadline_type: str  # Will be imported from enums
    due_date: datetime
    description: Optional[str] = None
    is_required: bool = True
    reminder_times: List[datetime] = field(default_factory=list)
    completed: bool = False
    completion_notes: Optional[str] = None
    
    def is_overdue(self) -> bool:
        """Check if deadline is overdue."""
        return datetime.now() > self.due_date and not self.completed
    
    def days_until_due(self) -> int:
        """Get days until deadline."""
        delta = self.due_date - datetime.now()
        return delta.days
    
    def hours_until_due(self) -> float:
        """Get hours until deadline."""
        delta = self.due_date - datetime.now()
        return delta.total_seconds() / 3600


@dataclass
class NotificationSettings:
    """User notification preferences."""
    email_notifications: bool = True
    desktop_notifications: bool = True
    project_updates: bool = True
    deadline_reminders: bool = True
    conflict_alerts: bool = True
    sync_status: bool = True
    email_address: str = ""
    notification_sound: bool = True
    timing: NotificationTiming = NotificationTiming.IMMEDIATE


@dataclass
class ValidationRules:
    """Configurable validation rules for different hackathons."""
    hackathon_id: str
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    file_size_limits: Dict[str, int] = field(default_factory=dict)
    allowed_file_types: List[str] = field(default_factory=list)
    max_team_size: int = 10
    min_team_size: int = 1
    custom_rules: Dict[str, Any] = field(default_factory=dict)

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Base Models',
            'description': 'base_models module for DevPost integration',
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
class DevpostConfig:
    """Devpost integration configuration."""
    api_base_url: str = "https://devpost.com/api"
    api_key: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3
    auto_sync: bool = True
    sync_interval: int = 300  # seconds
    debug_mode: bool = False
    log_level: str = "INFO"
    custom_headers: Dict[str, str] = field(default_factory=dict)
