from datetime import datetime
from typing import Dict, List, Any

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
    """Group of tasks that can execute in parallel."""
    group_id: str
    tasks: List[TaskNode]
    estimated_duration: int  # days
    coordination_overhead: float = 0.1  # 10% overhead by default
    resource_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass