#!/usr/bin/env python3
"""
Deadline Models - Deadline data models and enums

Extracted from deadline_tracker.py for RM-DDD compliance.
Single responsibility: Deadline data models and enumerations.
"""

import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime


logger = logging.getLogger(__name__)


class DeadlineStatus(Enum):
    """Deadline status enumeration."""
    UPCOMING = "upcoming"
    SOON = "soon"  # Within warning threshold
    OVERDUE = "overdue"
    COMPLETED = "completed"


class DeadlineType(Enum):
    """Deadline type enumeration."""
    SUBMISSION = "submission"
    JUDGING = "judging"
    REGISTRATION = "registration"
    FINAL_PRESENTATION = "final_presentation"
    CUSTOM = "custom"


@dataclass
class DeadlineInfo(ReflectiveModule):
    """Extended deadline information with status and requirements."""
    hackathon_id: str
    hackathon_name: str
    deadline_date: datetime
    submission_deadline: datetime
    judging_deadline: Optional[datetime]
    status: DeadlineStatus
    time_remaining: str
    requirements: List[Dict[str, Any]]
    is_registered: bool
    submission_status: str
    
    @property
    def is_overdue(self) -> bool:
        """Check if deadline is overdue."""
        return self.status == DeadlineStatus.OVERDUE
    
    @property
    def is_soon(self) -> bool:
        """Check if deadline is soon."""
        return self.status == DeadlineStatus.SOON
    
    @property
    def is_upcoming(self) -> bool:
        """Check if deadline is upcoming."""
        return self.status == DeadlineStatus.UPCOMING
    
    @property
    def is_completed(self) -> bool:
        """Check if deadline is completed."""
        return self.status == DeadlineStatus.COMPLETED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'hackathon_id': self.hackathon_id,
            'hackathon_name': self.hackathon_name,
            'deadline_date': self.deadline_date.isoformat(),
            'submission_deadline': self.submission_deadline.isoformat(),
            'judging_deadline': self.judging_deadline.isoformat() if self.judging_deadline else None,
            'status': self.status.value,
            'time_remaining': self.time_remaining,
            'requirements': self.requirements,
            'is_registered': self.is_registered,
            'submission_status': self.submission_status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeadlineInfo':
        """Create from dictionary."""
        return cls(
            hackathon_id=data['hackathon_id'],
            hackathon_name=data['hackathon_name'],
            deadline_date=datetime.fromisoformat(data['deadline_date']),
            submission_deadline=datetime.fromisoformat(data['submission_deadline']),
            judging_deadline=datetime.fromisoformat(data['judging_deadline']) if data.get('judging_deadline') else None,
            status=DeadlineStatus(data['status']),
            time_remaining=data['time_remaining'],
            requirements=data['requirements'],
            is_registered=data['is_registered'],
            submission_status=data['submission_status']
        )


@dataclass
class DeadlineAlert:
    """Deadline alert configuration."""
    alert_id: str
    deadline_id: str
    alert_time: datetime
    alert_type: str  # 'email', 'push', 'sms', 'in_app'
    message: str
    is_sent: bool = False
    sent_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def mark_sent(self) -> None:
        """Mark alert as sent."""
        self.is_sent = True
        self.sent_at = datetime.now()
    
    def can_retry(self) -> bool:
        """Check if alert can be retried."""
        return not self.is_sent and self.retry_count < self.max_retries
    
    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'alert_id': self.alert_id,
            'deadline_id': self.deadline_id,
            'alert_time': self.alert_time.isoformat(),
            'alert_type': self.alert_type,
            'message': self.message,
            'is_sent': self.is_sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeadlineAlert':
        """Create from dictionary."""
        return cls(
            alert_id=data['alert_id'],
            deadline_id=data['deadline_id'],
            alert_time=datetime.fromisoformat(data['alert_time']),
            alert_type=data['alert_type'],
            message=data['message'],
            is_sent=data.get('is_sent', False),
            sent_at=datetime.fromisoformat(data['sent_at']) if data.get('sent_at') else None,
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3)
        )


@dataclass
class DeadlineConfiguration:
    """Deadline tracking configuration."""
    warning_threshold_hours: int = 24
    critical_threshold_hours: int = 2
    check_interval_minutes: int = 30
    enable_notifications: bool = True
    notification_types: List[str] = None
    auto_register: bool = False
    auto_submit: bool = False
    backup_reminders: bool = True
    timezone: str = "UTC"
    
    def __post_init__(self):
        if self.notification_types is None:
            self.notification_types = ['email', 'in_app']
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'warning_threshold_hours': self.warning_threshold_hours,
            'critical_threshold_hours': self.critical_threshold_hours,
            'check_interval_minutes': self.check_interval_minutes,
            'enable_notifications': self.enable_notifications,
            'notification_types': self.notification_types,
            'auto_register': self.auto_register,
            'auto_submit': self.auto_submit,
            'backup_reminders': self.backup_reminders,
            'timezone': self.timezone
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeadlineConfiguration':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class DeadlineStatistics:
    """Deadline tracking statistics."""
    total_deadlines: int = 0
    upcoming_deadlines: int = 0
    soon_deadlines: int = 0
    overdue_deadlines: int = 0
    completed_deadlines: int = 0
    alerts_sent: int = 0
    alerts_failed: int = 0
    last_check: Optional[datetime] = None
    check_count: int = 0
    
    def update_counts(self, deadlines: List[DeadlineInfo]) -> None:
        """Update counts based on deadline list."""
        self.total_deadlines = len(deadlines)
        self.upcoming_deadlines = len([d for d in deadlines if d.is_upcoming])
        self.soon_deadlines = len([d for d in deadlines if d.is_soon])
        self.overdue_deadlines = len([d for d in deadlines if d.is_overdue])
        self.completed_deadlines = len([d for d in deadlines if d.is_completed])
        self.last_check = datetime.now()
        self.check_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_deadlines': self.total_deadlines,
            'upcoming_deadlines': self.upcoming_deadlines,
            'soon_deadlines': self.soon_deadlines,
            'overdue_deadlines': self.overdue_deadlines,
            'completed_deadlines': self.completed_deadlines,
            'alerts_sent': self.alerts_sent,
            'alerts_failed': self.alerts_failed,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'check_count': self.check_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeadlineStatistics':
        """Create from dictionary."""
        return cls(
            total_deadlines=data.get('total_deadlines', 0),
            upcoming_deadlines=data.get('upcoming_deadlines', 0),
            soon_deadlines=data.get('soon_deadlines', 0),
            overdue_deadlines=data.get('overdue_deadlines', 0),
            completed_deadlines=data.get('completed_deadlines', 0),
            alerts_sent=data.get('alerts_sent', 0),
            alerts_failed=data.get('alerts_failed', 0),
            last_check=datetime.fromisoformat(data['last_check']) if data.get('last_check') else None,
            check_count=data.get('check_count', 0)
        )

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Deadline Models',
            'description': 'deadline_models module for DevPost integration',
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
class DeadlineRequirement:
    """Deadline requirement specification."""
    requirement_id: str
    requirement_type: str  # 'file', 'form', 'video', 'presentation'
    title: str
    description: str
    is_required: bool = True
    file_types: List[str] = None
    max_file_size_mb: Optional[int] = None
    min_file_size_mb: Optional[int] = None
    due_date: Optional[datetime] = None
    completion_status: str = "pending"  # 'pending', 'in_progress', 'completed', 'overdue'
    
    def __post_init__(self):
        if self.file_types is None:
            self.file_types = []
    
    def is_completed(self) -> bool:
        """Check if requirement is completed."""
        return self.completion_status == "completed"
    
    def is_overdue(self) -> bool:
        """Check if requirement is overdue."""
        if not self.due_date:
            return False
        return datetime.now() > self.due_date and not self.is_completed()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'requirement_id': self.requirement_id,
            'requirement_type': self.requirement_type,
            'title': self.title,
            'description': self.description,
            'is_required': self.is_required,
            'file_types': self.file_types,
            'max_file_size_mb': self.max_file_size_mb,
            'min_file_size_mb': self.min_file_size_mb,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completion_status': self.completion_status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeadlineRequirement':
        """Create from dictionary."""
        return cls(
            requirement_id=data['requirement_id'],
            requirement_type=data['requirement_type'],
            title=data['title'],
            description=data['description'],
            is_required=data.get('is_required', True),
            file_types=data.get('file_types', []),
            max_file_size_mb=data.get('max_file_size_mb'),
            min_file_size_mb=data.get('min_file_size_mb'),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            completion_status=data.get('completion_status', 'pending')
        )
