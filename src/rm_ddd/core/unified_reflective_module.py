from src.rm_ddd.core.base_reflective_module import ReflectiveModule
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

# RDI Compliance Marker
RDI_COMPLIANT = True
UNIFIED_INTERFACE_VERSION = "1.0.0"
CANONICAL_SOURCE = "src/rm_ddd/core/unified_reflective_module.py"