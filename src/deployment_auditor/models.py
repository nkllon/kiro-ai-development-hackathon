"""
Core data models for the Deployment Data Governance Auditor.

This module defines the fundamental data structures used throughout the system
for representing file events, violations, and remediation results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import hashlib
import os


class EventType(Enum):
    """File system event types."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


class ViolationType(Enum):
    """Types of deployment data governance violations."""
    DATABASE_FILE = "database_file"
    TIME_SERIES_DATA = "time_series_data"
    LOG_FILE = "log_file"
    CACHE_FILE = "cache_file"
    RUNTIME_STATE = "runtime_state"
    BINARY_EXECUTABLE = "binary_executable"
    PLUGIN_DATA = "plugin_data"
    CREDENTIALS = "credentials"


class Severity(Enum):
    """Violation severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class FileMetadata:
    """Metadata about a file."""
    size: int
    permissions: str
    created_at: datetime
    modified_at: datetime
    file_hash: Optional[str] = None
    
    @classmethod
    def from_path(cls, file_path: str) -> 'FileMetadata':
        """Create FileMetadata from a file path."""
        try:
            stat = os.stat(file_path)
            file_hash = None
            
            # Calculate hash for small files only (< 1MB)
            if stat.st_size < 1024 * 1024:
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()[:16]
                except (IOError, OSError):
                    pass  # Hash calculation failed, continue without it
            
            return cls(
                size=stat.st_size,
                permissions=oct(stat.st_mode)[-3:],
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime),
                file_hash=file_hash
            )
        except (OSError, IOError) as e:
            # Return minimal metadata if file access fails
            return cls(
                size=0,
                permissions="000",
                created_at=datetime.now(),
                modified_at=datetime.now(),
                file_hash=None
            )


@dataclass
class FileEvent:
    """Represents a file system event."""
    event_type: EventType
    file_path: str
    timestamp: datetime
    file_size: int
    file_hash: Optional[str] = None
    
    @classmethod
    def create_event(cls, event_type: EventType, file_path: str) -> 'FileEvent':
        """Create a FileEvent with current timestamp and file metadata."""
        metadata = FileMetadata.from_path(file_path)
        return cls(
            event_type=event_type,
            file_path=file_path,
            timestamp=datetime.now(),
            file_size=metadata.size,
            file_hash=metadata.file_hash
        )


@dataclass
class Violation:
    """Represents a deployment data governance violation."""
    file_path: str
    pattern_matched: str
    violation_type: ViolationType
    detected_at: datetime
    file_metadata: FileMetadata
    
    @classmethod
    def create_violation(
        cls, 
        file_path: str, 
        pattern_matched: str, 
        violation_type: ViolationType
    ) -> 'Violation':
        """Create a Violation with current timestamp and file metadata."""
        return cls(
            file_path=file_path,
            pattern_matched=pattern_matched,
            violation_type=violation_type,
            detected_at=datetime.now(),
            file_metadata=FileMetadata.from_path(file_path)
        )


@dataclass
class RemediationStep:
    """A single step in the remediation process."""
    action: str
    description: str
    command: Optional[str] = None
    automated: bool = False


@dataclass
class ImpactAssessment:
    """Assessment of violation impact."""
    security_risk: int  # 1-10 scale
    compliance_risk: int  # 1-10 scale
    performance_impact: int  # 1-10 scale
    description: str


@dataclass
class ClassifiedViolation:
    """A violation with classification and remediation guidance."""
    violation: Violation
    severity: Severity
    risk_score: int
    remediation_steps: List[RemediationStep]
    estimated_impact: ImpactAssessment
    
    @property
    def file_path(self) -> str:
        """Convenience property to access file path."""
        return self.violation.file_path
    
    @property
    def violation_type(self) -> ViolationType:
        """Convenience property to access violation type."""
        return self.violation.violation_type


@dataclass
class RemediationAction:
    """An action taken during remediation."""
    action_type: str
    target: str
    timestamp: datetime
    success: bool
    details: str


@dataclass
class RemediationResult:
    """Result of a remediation attempt."""
    violation_id: str
    actions_taken: List[RemediationAction]
    success: bool
    error_message: Optional[str] = None
    follow_up_required: bool = False
    
    def add_action(self, action_type: str, target: str, success: bool, details: str):
        """Add a remediation action to the result."""
        action = RemediationAction(
            action_type=action_type,
            target=target,
            timestamp=datetime.now(),
            success=success,
            details=details
        )
        self.actions_taken.append(action)


@dataclass
class MonitoringStatus:
    """Status of file system monitoring."""
    is_active: bool
    watched_paths: List[str]
    events_processed: int
    violations_detected: int
    last_scan: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)


@dataclass
class ComplianceReport:
    """Comprehensive compliance report."""
    scan_timestamp: datetime
    total_files_scanned: int
    violations_found: int
    violations_by_severity: Dict[Severity, int]
    violations_by_type: Dict[ViolationType, int]
    remediation_summary: Dict[str, int]
    recommendations: List[str]
    
    def add_violation(self, violation: ClassifiedViolation):
        """Add a violation to the report statistics."""
        self.violations_found += 1
        
        # Update severity counts
        if violation.severity not in self.violations_by_severity:
            self.violations_by_severity[violation.severity] = 0
        self.violations_by_severity[violation.severity] += 1
        
        # Update type counts
        if violation.violation_type not in self.violations_by_type:
            self.violations_by_type[violation.violation_type] = 0
        self.violations_by_type[violation.violation_type] += 1


@dataclass
class ConfigurationSchema:
    """Configuration schema for the deployment auditor."""
    monitoring: Dict[str, Any] = field(default_factory=dict)
    patterns: Dict[str, Any] = field(default_factory=dict)
    remediation: Dict[str, Any] = field(default_factory=dict)
    notifications: Dict[str, Any] = field(default_factory=dict)
    prometheus: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def default_config(cls) -> 'ConfigurationSchema':
        """Create default configuration."""
        return cls(
            monitoring={
                "watch_paths": ["deployment/"],
                "excluded_paths": ["deployment/docs/"],
                "scan_interval": 60
            },
            patterns={
                "database_files": {
                    "patterns": ["*.db", "*.sqlite*", "*.sql"],
                    "severity": "CRITICAL"
                },
                "time_series_data": {
                    "patterns": ["*prometheus-data*", "*grafana-data*"],
                    "severity": "HIGH"
                },
                "log_files": {
                    "patterns": ["*.log", "logs/", "log/"],
                    "severity": "MEDIUM"
                }
            },
            remediation={
                "auto_gitignore": True,
                "auto_quarantine": True,
                "git_integration": True
            },
            notifications={
                "slack": {"enabled": False},
                "email": {"enabled": False}
            },
            prometheus={
                "enabled": True,
                "port": 9090,
                "metrics_prefix": "deployment_auditor_"
            }
        )