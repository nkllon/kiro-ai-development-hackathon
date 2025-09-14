from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Systematic resource allocation plan."""
    teams: List[TeamAssignment]
    resource_utilization: float
    bottleneck_resources: List[str] = field(default_factory=list)
    scaling_recommendations: List[str] = field(default_factory=list)
    