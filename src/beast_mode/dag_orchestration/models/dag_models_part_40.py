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
    """Optimal route to MVP delivery."""
    route_id: str
    phases: List[MVPPhase]
    critical_tasks: List[TaskNode]
    total_estimated_effort: int  # hours
    estimated_timeline: int  # weeks
    success_probability: float
    risk_factors: List[RiskFactor] = field(default_factory=list)
    