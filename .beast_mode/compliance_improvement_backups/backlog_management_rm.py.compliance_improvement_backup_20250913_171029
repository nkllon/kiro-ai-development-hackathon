"""
BacklogManagementRM - Central orchestration of backlog operations with RM compliance

This module implements the primary RM for the OpenFlow Backlog Management System,
providing centralized orchestration of backlog operations while maintaining
full RM compliance with the Beast Mode framework.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import time

from ..core.reflective_module import ReflectiveModule, HealthStatus
from .models import BacklogItem, MPMValidation
from .enums import BeastReadinessStatus, StrategicTrack
from .health_monitoring import BacklogHealthMonitor
from .operational_status import BacklogOperationalStatus
from .placeholders import BacklogItemSpec, ReadinessResult
from .core_operations import BacklogCoreOperations


class BacklogManagementRM(ReflectiveModule):
    """
    Central orchestration of backlog operations with RM compliance
    
    Responsibilities:
    - Orchestrate backlog item lifecycle management
    - Enforce beast-readiness criteria
    - Coordinate with Ghostbusters validation
    - Provide MPM interface for strategic management
    - Maintain RM compliance and health monitoring
    """
    
    def __init__(self):
        super().__init__("BacklogManagementRM")
        self._backlog_items: Dict[str, BacklogItem] = {}
        self._degradation_mode = False
        self._initialization_time = time.time()
        
        # Initialize helper components
        self._health_monitor = BacklogHealthMonitor()
        self._status_reporter = BacklogOperationalStatus("BacklogManagementRM", self._initialization_time)
        self._core_operations = BacklogCoreOperations(
            self.logger, 
            self._health_monitor, 
            lambda: self._degradation_mode
        )
        
        # Initialize health indicators
        self._health_monitor.update_health_indicator(
            "initialization", 
            HealthStatus.HEALTHY, 
            True, 
            "BacklogManagementRM initialized successfully"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """
        Operational visibility - external status reporting for GKE queries
        Required by R6.4 - external systems get accurate operational information
        """
        return self._status_reporter.generate_module_status(
            self._backlog_items,
            self.is_healthy(),
            self._degradation_mode,
            self._health_monitor.get_performance_metrics()
        )
        
    def is_healthy(self) -> bool:
        """
        Self-monitoring - accurate health assessment
        Required by R6.2 - components report health status accurately
        """
        try:
            # Check basic operational health
            if self._degradation_mode:
                return False
                
            # Check performance constraints (C-05: <500ms response)
            if not self._health_monitor.is_performance_healthy():
                return False
                
            # Check data consistency
            if not self._health_monitor.validate_data_consistency(self._backlog_items):
                return False
                
            # Check memory usage (basic check)
            if len(self._backlog_items) > 10000:  # Arbitrary large number
                self.logger.warning("Large number of backlog items may impact performance")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False
            
    def get_health_indicators(self) -> Dict[str, Any]:
        """
        Self-reporting - detailed health metrics for operational visibility
        Required by R6.2 - components report health status accurately
        """
        # Update performance health indicator
        metrics = self._health_monitor.get_performance_metrics()
        avg_response_time = metrics["avg_response_time"]
        
        perf_status = HealthStatus.HEALTHY
        perf_message = "Performance within acceptable limits"
        
        if avg_response_time > 0.5:
            perf_status = HealthStatus.UNHEALTHY
            perf_message = f"Average response time {avg_response_time:.3f}s exceeds 500ms limit"
        elif avg_response_time > 0.3:
            perf_status = HealthStatus.DEGRADED
            perf_message = f"Average response time {avg_response_time:.3f}s approaching limit"
            
        self._health_monitor.update_health_indicator(
            "performance", perf_status, avg_response_time, perf_message
        )
        
        # Update data consistency health indicator
        consistency_healthy = self._health_monitor.validate_data_consistency(self._backlog_items)
        self._health_monitor.update_health_indicator(
            "data_consistency",
            HealthStatus.HEALTHY if consistency_healthy else HealthStatus.UNHEALTHY,
            consistency_healthy,
            "Data consistency validated" if consistency_healthy else "Data consistency issues detected"
        )
        
        # Update capacity health indicator
        capacity_ratio = len(self._backlog_items) / 10000  # Assume 10k is max capacity
        capacity_status = self._health_monitor.calculate_capacity_status(len(self._backlog_items))
            
        self._health_monitor.update_health_indicator(
            "capacity", capacity_status, capacity_ratio, f"Using {capacity_ratio:.1%} of estimated capacity"
        )
        
        health_indicators = self._health_monitor.get_health_indicators()
        return {
            "health_indicators": {
                name: {
                    "status": indicator.status.value,
                    "value": indicator.value,
                    "message": indicator.message,
                    "timestamp": indicator.timestamp
                }
                for name, indicator in health_indicators.items()
            },
            "overall_health": self.is_healthy(),
            "degradation_active": self._degradation_mode,
            "metrics": metrics
        }
        
    def _get_primary_responsibility(self) -> str:
        """Define the single primary responsibility of this module"""
        return "Central orchestration of backlog operations with RM compliance"
        
    def _check_boundary_violations(self) -> List[str]:
        """Check for architectural boundary violations"""
        violations = []
        
        # Check if we're doing dependency management (should be delegated)
        # Check if we're doing validation (should be delegated to Ghostbusters)
        # Check if we're doing direct data persistence (should be abstracted)
        
        # For now, return empty as this is the base implementation
        return violations
        

        
    # Core backlog operations (delegated to BacklogCoreOperations)
    
    def create_backlog_item(self, item_spec: BacklogItemSpec) -> BacklogItem:
        """Create a new backlog item with validation"""
        return self._core_operations.create_backlog_item(item_spec, len(self._backlog_items))
            
    def mark_beast_ready(self, item_id: str, mpm_validation: MPMValidation) -> ReadinessResult:
        """Mark an item as beast-ready after MPM validation"""
        return self._core_operations.mark_beast_ready(item_id, mpm_validation)


