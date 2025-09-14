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
    """Systematic execution results with quality metrics."""
    execution_id: str
    status: ExecutionStatus
    completed_tasks: List[str]
    failed_tasks: List[str]
    systematic_quality_score: float
    execution_time: int  # minutes
    lessons_learned: List[str] = field(default_factory=list)
    