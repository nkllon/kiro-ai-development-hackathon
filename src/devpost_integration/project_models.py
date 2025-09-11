#!/usr/bin/env python3
"""
Project Models - Project-related data classes

Extracted from models.py for RM-DDD compliance.
Single responsibility: Project-related data classes and models.
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

    SubmissionStatus, MediaType, TeamMember, ProjectLink, 
    MediaFile, SubmissionRequirement, SyncOperation, 
    FileChangeEvent, Deadline, DevpostConfig
)


@dataclass
class DevpostProject(ReflectiveModule):
    """Complete Devpost project information."""
    project_id: str
    title: str
    description: str
    technologies: List[str] = field(default_factory=list)
    team_members: List[TeamMember] = field(default_factory=list)
    links: List[ProjectLink] = field(default_factory=list)
    media_files: List[MediaFile] = field(default_factory=list)
    submission_status: SubmissionStatus = SubmissionStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    hackathon_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectMetadata:
    """Local project metadata extracted from files."""
    project_id: str
    title: str
    description: str
    technologies: List[str] = field(default_factory=list)
    team_members: List[TeamMember] = field(default_factory=list)
    links: List[ProjectLink] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    project_path: str = ""
    last_modified: datetime = field(default_factory=datetime.now)
    file_count: int = 0
    total_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectSummary:
    """Summary information for multi-project management."""
    project_id: str
    title: str
    status: str
    last_activity: datetime
    team_size: int = 0
    file_count: int = 0
    completion_percentage: float = 0.0
    deadline_status: str = "unknown"
    sync_status: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncResult:
    """Result of a synchronization operation."""
    success: bool
    operation_id: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    files_processed: int = 0
    files_failed: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    score: float
    issues_count: int
    critical_issues: int = 0
    warnings: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class PreviewData:
    """Data for preview generation."""
    project_id: str
    title: str
    description: str
    technologies: List[str] = field(default_factory=list)
    team_members: List[TeamMember] = field(default_factory=list)
    links: List[ProjectLink] = field(default_factory=list)
    media_files: List[MediaFile] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    preview_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectStatus:
    """Current project status information."""
    project_id: str
    is_active: bool
    last_sync: Optional[datetime] = None
    sync_status: str = "unknown"
    validation_status: str = "unknown"
    completion_status: str = "unknown"
    file_count: int = 0
    last_activity: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthResult:
    """Authentication result."""
    success: bool
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConnectionResult:
    """Project connection result."""
    success: bool
    project_id: str
    devpost_project_id: Optional[str] = None
    connection_url: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FormattingIssue:
    """Preview formatting issue."""
    issue_type: str
    severity: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Project Models',
            'description': 'project_models module for DevPost integration',
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
class CompletionDetails:
    """Project completion status details."""
    project_id: str
    completion_percentage: float
    completed_requirements: List[str] = field(default_factory=list)
    pending_requirements: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None
    blockers: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
