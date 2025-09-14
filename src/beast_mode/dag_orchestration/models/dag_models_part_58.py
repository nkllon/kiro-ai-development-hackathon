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
    """Optimized parallel execution plan."""
    execution_id: str
    execution_phases: List[ExecutionPhase]
    resource_allocation: ResourceAllocation
    parallel_groups: List[ParallelGroup]
    estimated_timeline: int  # weeks
    maximum_parallelism: int  # concurrent tasks
    bottlenecks: List[str] = field(default_factory=list)


@dataclass