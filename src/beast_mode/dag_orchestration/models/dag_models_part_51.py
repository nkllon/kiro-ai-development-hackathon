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
    """Team assignment for execution."""
    team_name: str
    team_members: List[str]
    assigned_tasks: List[str]  # task IDs
    capabilities: List[str]
    availability: float  # 0.0 to 1.0


@dataclass