#!/usr/bin/env python3
"""
Base ReflectiveModule class - RDI Compliant
This is the SINGLE, CANONICAL base class for all ReflectiveModule implementations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass


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

    # SCA capabilities
    SCA_ANALYSIS = "sca_analysis"
    COMPLIANCE_CHECKING = "compliance_checking"
    RANDOM_ATTACK = "random_attack"
    EFFICIENCY_ANALYSIS = "efficiency_analysis"
    BEAST_MODE = "beast_mode"


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


class ReflectiveModule(ABC):
    """
    Base ReflectiveModule class - RDI Compliant

    This is the SINGLE, CANONICAL base class for all ReflectiveModule implementations.
    Provides systematic compliance, health monitoring, and registry integration.
    """


def __init__(self, module_name: str, version: str = "1.0.0"):
    """Initialize the reflective module - RDI Compliant"""
    self.module_name = module_name
    self.version = version
    self.module_id = f"{module_name}_{self.__class__.__name__}"
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

    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration - RDI Compliant"""
        return {
            "module_name": self.module_name,
            "version": self.version,
            "module_id": self.module_id,
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics - RDI Compliant"""
        return {
            "uptime_seconds": self.get_uptime_seconds(),
            "error_count": self._error_count,
            "warning_count": self._warning_count,
            "last_activity": self._last_activity.isoformat(),
        }

    def is_healthy(self) -> bool:
        """Check if module is healthy - RDI Compliant"""
        health = self.check_health()
        return health.status == ModuleStatus.HEALTHY

    def get_module_status(self) -> ModuleStatus:
        """Get module status - RDI Compliant"""
        health = self.check_health()
        return health.status

    def get_health_indicators(self) -> Dict[str, Any]:
        """Get health indicators - RDI Compliant"""
        health = self.check_health()
        return {
            "status": health.status.value,
            "health_score": health.health_score,
            "issues": health.issues,
            "uptime_seconds": health.uptime_seconds,
            "error_count": health.error_count,
            "warning_count": health.warning_count,
        }

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

    def get_interface_metadata(self) -> Dict[str, Any]:
        """Get interface metadata for registry - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "interface_type": self.__class__.__name__,
            "version": self.version,
            "dependencies": self.get_dependencies(),
            "capabilities": [cap.value for cap in self.get_capabilities()],
        }

    def register_module(self, registry) -> None:
        """Register module with registry - RDI Compliant"""
        if hasattr(registry, "register"):
            registry.register(self.get_interface_metadata())

    def health_check(self) -> Dict[str, Any]:
        """Perform health check - RDI Compliant"""
        health = self.check_health()
        return {
            "status": health.status.value,
            "timestamp": datetime.now().isoformat(),
            "module_id": self.module_id,
            "health_score": health.health_score,
            "issues": health.issues,
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status - RDI Compliant"""
        return self.health_check()

    # RDI Compliance Marker
    RDI_COMPLIANT = True
    UNIFIED_INTERFACE_VERSION = "1.0.0"
    CANONICAL_SOURCE = "src/rm_ddd/core/base_reflective_module.py"
