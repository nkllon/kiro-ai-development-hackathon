"""
Unified ReflectiveModule Interface - RDI Compliant

This is the SINGLE, CANONICAL ReflectiveModule interface for the entire RM-DDD framework.
All other ReflectiveModule definitions are deprecated and should be replaced with this one.

RDI Compliance:
- Single source of truth for ReflectiveModule interface
- Unified method signatures across all components
- Consistent health monitoring and capability tracking
- Eliminates interface duplication and conflicts
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional


class ModuleStatus(Enum):
    """Module operational status - RDI Compliant"""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class ModuleCapability(Enum):
    """Module capability types - RDI Compliant"""
    # Core capabilities
    CORE_FUNCTIONALITY = "core_functionality"
    DATA_PROCESSING = "data_processing"
    API_INTEGRATION = "api_integration"
    FILE_OPERATIONS = "file_operations"
    VALIDATION = "validation"
    MONITORING = "monitoring"
    
    # DevPost integration capabilities
    SYNC_OPERATIONS = "sync_operations"
    PROGRESS_TRACKING = "progress_tracking"
    ERROR_HANDLING = "error_handling"
    STATUS_MONITORING = "status_monitoring"
    METADATA_MANAGEMENT = "metadata_management"
    CONFIG_MANAGEMENT = "config_management"
    EXPORT_IMPORT = "export_import"
    PROJECT_MANAGEMENT = "project_management"
    TEAM_MANAGEMENT = "team_management"
    SUBMISSION_TRACKING = "submission_tracking"
    DEADLINE_MANAGEMENT = "deadline_management"
    MEMBER_MANAGEMENT = "member_management"
    ROLE_MANAGEMENT = "role_management"
    PERMISSION_CONTROL = "permission_control"
    SETTINGS_MANAGEMENT = "settings_management"
    TIMING_CONTROL = "timing_control"
    CHANNEL_MANAGEMENT = "channel_management"
    PREFERENCE_CONTROL = "preference_control"
    MESSAGE_MANAGEMENT = "message_management"
    DELIVERY_TRACKING = "delivery_tracking"
    RECIPIENT_MANAGEMENT = "recipient_management"
    RESULT_TRACKING = "result_tracking"
    METRICS_COLLECTION = "metrics_collection"
    REPORTING = "reporting"
    EVENT_TRACKING = "event_tracking"
    CHANGE_DETECTION = "change_detection"
    ISSUE_TRACKING = "issue_tracking"
    SUGGESTION_PROVIDER = "suggestion_provider"
    SEVERITY_ASSESSMENT = "severity_assessment"
    
    # Beast mode capabilities
    SYSTEMATIC_ANALYSIS = "systematic_analysis"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    FAILURE_RECOVERY = "failure_recovery"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    QUALITY_ASSURANCE = "quality_assurance"
    COMPLIANCE_MONITORING = "compliance_monitoring"
    REFACTORING_OPERATIONS = "refactoring_operations"
    DEPENDENCY_MANAGEMENT = "dependency_management"
    MIGRATION_SUPPORT = "migration_support"
    BOOTSTRAP_ORCHESTRATION = "bootstrap_orchestration"
    PARALLEL_COORDINATION = "parallel_coordination"
    METRICS_EVALUATION = "metrics_evaluation"
    ORGANIZATION_MANAGEMENT = "organization_management"
    SELF_REFACTORING = "self_refactoring"
    SYSTEMATIC_CLEANUP = "systematic_cleanup"
    
    # Multi-instance orchestration capabilities
    INSTANCE_MANAGEMENT = "instance_management"
    LOAD_BALANCING = "load_balancing"
    RESOURCE_ALLOCATION = "resource_allocation"
    SCALING_OPERATIONS = "scaling_operations"
    FAILOVER_MANAGEMENT = "failover_management"
    CLUSTER_COORDINATION = "cluster_coordination"


@dataclass
class ModuleHealth:
    """Module health information - RDI Compliant"""
    module_id: str
    status: ModuleStatus
    health_score: float  # 0.0 to 1.0
    issues: List[str]
    capabilities: List[ModuleCapability]
    dependencies: List[str]
    metrics: Dict[str, Any]
    last_check: datetime
    uptime_seconds: float = 0.0
    error_count: int = 0
    warning_count: int = 0


@dataclass
class GracefulDegradationResult:
    """Result of graceful degradation - RDI Compliant"""
    success: bool
    degraded_capabilities: List[ModuleCapability]
    remaining_capabilities: List[ModuleCapability]
    error_message: Optional[str] = None
    recovery_actions: List[str] = None


class ReflectiveModule(ABC):
    """
    Unified ReflectiveModule Interface - RDI Compliant
    
    This is the SINGLE, CANONICAL interface for all reflective modules
    in the RM-DDD framework. All modules must implement this interface.
    
    RDI Compliance:
    - Single source of truth
    - Unified method signatures
    - Consistent behavior across all components
    - Eliminates interface duplication
    """
    
    def __init__(self, module_name: str, version: str = "1.0.0"):
        """Initialize the reflective module - RDI Compliant"""
        self.module_name = module_name
        self.version = version
        self._start_time = datetime.now()
        self._last_activity = datetime.now()
        self._error_count = 0
        self._warning_count = 0
    
    @abstractmethod
    def get_module_info(self) -> Dict[str, Any]:
        """
        Get module information - RDI Compliant
        
        Returns:
            Dict containing module metadata (id, version, description, etc.)
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[ModuleCapability]:
        """
        Get module capabilities - RDI Compliant
        
        Returns:
            List of ModuleCapability enums this module supports
        """
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """
        Get module dependencies - RDI Compliant
        
        Returns:
            List of module IDs this module depends on
        """
        pass
    
    @abstractmethod
    def check_health(self) -> ModuleHealth:
        """
        Check module health - RDI Compliant
        
        Returns:
            ModuleHealth object with current health status
        """
        pass
    
    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get module configuration - RDI Compliant
        
        Returns:
            Dict containing current configuration
        """
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get module metrics - RDI Compliant
        
        Returns:
            Dict containing performance and operational metrics
        """
        pass
    
    def is_healthy(self) -> bool:
        """
        Check if module is healthy - RDI Compliant
        
        Returns:
            True if module is healthy, False otherwise
        """
        health = self.check_health()
        return health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING]
    
    def get_module_status(self) -> ModuleStatus:
        """
        Get module status - RDI Compliant
        
        Returns:
            Current ModuleStatus
        """
        health = self.check_health()
        return health.status
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """
        Get health indicators - RDI Compliant
        
        Returns:
            Dict containing health indicators and metrics
        """
        health = self.check_health()
        return {
            "status": health.status.value,
            "health_score": health.health_score,
            "issues": health.issues,
            "uptime_seconds": health.uptime_seconds,
            "error_count": health.error_count,
            "warning_count": health.warning_count
        }
    
    def degrade_gracefully(self, failure_context: Dict[str, Any]) -> GracefulDegradationResult:
        """
        Handle graceful degradation - RDI Compliant
        
        Args:
            failure_context: Context about the failure
            
        Returns:
            GracefulDegradationResult with degradation details
        """
        # Default implementation - modules can override
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities(),
            error_message="Graceful degradation not implemented",
            recovery_actions=[]
        )
    
    def update_activity(self) -> None:
        """Update last activity timestamp - RDI Compliant"""
        self._last_activity = datetime.now()
    
    def get_uptime_seconds(self) -> float:
        """Get module uptime in seconds - RDI Compliant"""
        return (datetime.now() - self._start_time).total_seconds()
    
    def increment_error_count(self) -> None:
        """Increment error count - RDI Compliant"""
        self._error_count += 1
    
    def increment_warning_count(self) -> None:
        """Increment warning count - RDI Compliant"""
        self._warning_count += 1
    
    def reset_metrics(self) -> None:
        """Reset module metrics - RDI Compliant"""
        self._error_count = 0
        self._warning_count = 0
        self._start_time = datetime.now()
        self._last_activity = datetime.now()


# RDI Compliance Marker
RDI_COMPLIANT = True
UNIFIED_INTERFACE_VERSION = "1.0.0"
CANONICAL_SOURCE = "src/rm_ddd/core/unified_reflective_module.py"

