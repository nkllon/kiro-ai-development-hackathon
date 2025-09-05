"""
Health monitoring utilities for BacklogManagementRM

This module provides health monitoring and performance tracking
functionality for the backlog management system.
"""

from typing import Dict, Any
import time
from ..core.reflective_module import HealthStatus, HealthIndicator


class BacklogHealthMonitor:
    """
    Health monitoring and performance tracking for backlog operations
    
    Responsibilities:
    - Track performance metrics
    - Monitor system health indicators
    - Detect performance degradation
    - Validate data consistency
    """
    
    def __init__(self):
        self._performance_metrics = {
            "total_items": 0,
            "beast_ready_items": 0,
            "avg_response_time": 0.0,
            "last_operation_time": 0.0
        }
        self._health_indicators: Dict[str, HealthIndicator] = {}
        
    def record_operation_time(self, operation_time: float):
        """Record operation time for performance monitoring"""
        self._performance_metrics["last_operation_time"] = time.time()
        
        # Update rolling average with higher weight for new values
        current_avg = self._performance_metrics["avg_response_time"]
        self._performance_metrics["avg_response_time"] = (current_avg * 0.7) + (operation_time * 0.3)
        
    def is_performance_healthy(self) -> bool:
        """Check if performance is within acceptable limits"""
        return self._performance_metrics["avg_response_time"] <= 0.5  # 500ms limit
        
    def validate_data_consistency(self, backlog_items: Dict[str, Any]) -> bool:
        """Validate internal data consistency"""
        try:
            for item_id, item in backlog_items.items():
                if not item:
                    continue
                if hasattr(item, 'item_id') and item.item_id != item_id:
                    return False
                if hasattr(item, 'title') and hasattr(item, 'created_by'):
                    if not item.title or not item.created_by:
                        return False
            return True
        except Exception:
            return False
            
    def update_health_indicator(self, name: str, status: HealthStatus, value: Any, message: str):
        """Update a health indicator with current status"""
        self._health_indicators[name] = HealthIndicator(
            name=name,
            status=status,
            value=value,
            message=message,
            timestamp=time.time()
        )
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self._performance_metrics.copy()
        
    def get_health_indicators(self) -> Dict[str, HealthIndicator]:
        """Get current health indicators"""
        return self._health_indicators.copy()
        
    def calculate_capacity_status(self, item_count: int, max_capacity: int = 10000) -> HealthStatus:
        """Calculate capacity health status"""
        capacity_ratio = item_count / max_capacity
        if capacity_ratio > 0.9:
            return HealthStatus.UNHEALTHY
        elif capacity_ratio > 0.7:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY