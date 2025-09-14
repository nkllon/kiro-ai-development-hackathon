"""
Unified ReflectiveModule Interface - RDI Compliant

This is the SINGLE, CANONICAL ReflectiveModule interface for:
- RDI Compliance
- Single source of truth
- Unified method signatures
- Consistent behavior across all components
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional

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
    CORE_FUNCTIONALITY = "core_functionality"
    DATA_PROCESSING = "data_processing"
    API_INTEGRATION = "api_integration"
    VALIDATION = "validation"
    MONITORING = "monitoring"

@dataclass
class ModuleHealth:
    """Module health information - RDI Compliant"""
    module_id: str
    status: ModuleStatus
    health_score: float
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
    """Unified ReflectiveModule Interface - RDI Compliant"""
    
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
        """Get module information - RDI Compliant"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        pass

    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Get module dependencies - RDI Compliant"""
        pass

    @abstractmethod
    def check_health(self) -> ModuleHealth:
        """Check module health - RDI Compliant"""
        pass

    def is_healthy(self) -> bool:
        """Check if module is healthy - RDI Compliant"""
        health = self.check_health()
        return health.status == ModuleStatus.HEALTHY

    def get_module_status(self) -> ModuleStatus:
        """Get module status - RDI Compliant"""
        health = self.check_health()
        return health.status

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