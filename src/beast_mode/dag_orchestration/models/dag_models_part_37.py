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
    """Systematic MVP phase with deliverables."""
    phase_name: str
    phase_number: int
    objectives: List[str]
    tasks: List[TaskNode]
    deliverables: List[str]
    estimated_duration: int  # weeks
    parallel_groups: List[ParallelGroup] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    dependencies_satisfied: List[str] = field(default_factory=list)


@dataclass