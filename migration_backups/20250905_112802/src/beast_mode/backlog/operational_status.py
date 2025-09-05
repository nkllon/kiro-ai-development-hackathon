"""
Operational status reporting for BacklogManagementRM

This module provides operational visibility and status reporting
functionality for external systems and GKE queries.
"""

from typing import Dict, Any, List
import time
from .enums import BeastReadinessStatus


class BacklogOperationalStatus:
    """
    Operational status reporting and visibility
    
    Responsibilities:
    - Generate module status reports
    - Provide operational capabilities information
    - Track managed strategic tracks
    - Support external system queries
    """
    
    def __init__(self, module_name: str, initialization_time: float):
        self.module_name = module_name
        self.initialization_time = initialization_time
        
    def generate_module_status(
        self, 
        backlog_items: Dict[str, Any], 
        is_healthy: bool, 
        degradation_mode: bool,
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive module status for external systems"""
        current_time = time.time()
        uptime = current_time - self.initialization_time
        
        return {
            "module_name": self.module_name,
            "status": "healthy" if is_healthy else "degraded",
            "uptime_seconds": uptime,
            "total_backlog_items": len(backlog_items),
            "beast_ready_items": self._count_beast_ready_items(backlog_items),
            "degradation_active": degradation_mode,
            "last_operation_timestamp": performance_metrics.get("last_operation_time", 0.0),
            "avg_response_time_ms": performance_metrics.get("avg_response_time", 0.0) * 1000,
            "tracks_managed": self._get_managed_tracks(backlog_items),
            "operational_capabilities": self._get_operational_capabilities(degradation_mode)
        }
        
    def _count_beast_ready_items(self, backlog_items: Dict[str, Any]) -> int:
        """Count items that are beast-ready"""
        return sum(
            1 for item in backlog_items.values() 
            if item and hasattr(item, 'beast_readiness_status') 
            and item.beast_readiness_status == BeastReadinessStatus.BEAST_READY
        )
        
    def _get_managed_tracks(self, backlog_items: Dict[str, Any]) -> List[str]:
        """Get list of strategic tracks being managed"""
        return list(set(
            item.track.value for item in backlog_items.values() 
            if item and hasattr(item, 'track')
        ))
        
    def _get_operational_capabilities(self, degradation_mode: bool) -> List[str]:
        """Get list of current operational capabilities"""
        capabilities = ["backlog_item_management", "health_monitoring"]
        
        if not degradation_mode:
            capabilities.extend([
                "beast_readiness_validation",
                "mpm_interface", 
                "performance_monitoring"
            ])
        else:
            capabilities.append("graceful_degradation_active")
            
        return capabilities