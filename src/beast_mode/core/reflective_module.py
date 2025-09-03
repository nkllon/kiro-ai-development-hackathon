"""
Beast Mode Framework - Reflective Module Base Class
Implements RM interface compliance as required by C-01 constraint
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
import logging

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthIndicator:
    name: str
    status: HealthStatus
    value: Any
    message: str
    timestamp: float

@dataclass
class GracefulDegradationResult:
    degradation_applied: bool
    reduced_functionality: list[str]
    recovery_strategy: str
    estimated_recovery_time: Optional[float]

class ReflectiveModule(ABC):
    """
    Base class implementing RM interface compliance (Constraint C-01)
    All Beast Mode components MUST inherit from this class
    """
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.logger = logging.getLogger(f"beast_mode.{module_name}")
        self._health_indicators: Dict[str, HealthIndicator] = {}
        self._degradation_active = False
        
    @abstractmethod
    def get_module_status(self) -> Dict[str, Any]:
        """
        Operational visibility - external status reporting for GKE queries
        Required by R6.4 - external systems get accurate operational information
        """
        pass
        
    @abstractmethod  
    def is_healthy(self) -> bool:
        """
        Self-monitoring - accurate health assessment
        Required by R6.2 - components report health status accurately
        """
        pass
        
    @abstractmethod
    def get_health_indicators(self) -> Dict[str, Any]:
        """
        Self-reporting - detailed health metrics for operational visibility
        Required by R6.2 - components report health status accurately
        """
        pass
        
    def degrade_gracefully(self, failure_context: Dict[str, Any]) -> GracefulDegradationResult:
        """
        Degrade gracefully without killing the system
        Required by R6.3 - components degrade gracefully without killing system
        """
        self.logger.warning(f"Graceful degradation triggered: {failure_context}")
        self._degradation_active = True
        
        # Default graceful degradation strategy
        reduced_functionality = ["advanced_features", "non_critical_operations"]
        recovery_strategy = "automatic_retry_with_exponential_backoff"
        
        return GracefulDegradationResult(
            degradation_applied=True,
            reduced_functionality=reduced_functionality,
            recovery_strategy=recovery_strategy,
            estimated_recovery_time=30.0  # 30 seconds default
        )
        
    def maintain_single_responsibility(self) -> Dict[str, Any]:
        """
        Validate component maintains single responsibility and clear boundaries
        Required by R6.5 - components maintain clear boundaries and single responsibility
        """
        return {
            "module_name": self.module_name,
            "primary_responsibility": self._get_primary_responsibility(),
            "boundary_violations": self._check_boundary_violations(),
            "single_responsibility_score": self._calculate_responsibility_score()
        }
        
    @abstractmethod
    def _get_primary_responsibility(self) -> str:
        """Define the single primary responsibility of this module"""
        pass
        
    def _check_boundary_violations(self) -> list[str]:
        """Check for architectural boundary violations"""
        # Default implementation - subclasses should override
        return []
        
    def _calculate_responsibility_score(self) -> float:
        """Calculate single responsibility adherence score (0.0-1.0)"""
        violations = self._check_boundary_violations()
        if not violations:
            return 1.0
        return max(0.0, 1.0 - (len(violations) * 0.2))
        
    def _update_health_indicator(self, name: str, status: HealthStatus, value: Any, message: str):
        """Update a health indicator with current status"""
        self._health_indicators[name] = HealthIndicator(
            name=name,
            status=status,
            value=value,
            message=message,
            timestamp=time.time()
        )