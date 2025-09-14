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
    """Analysis of presentation timing."""
    total_duration: int
    section_durations: Dict[str, int]
    pacing_score: float
    timing_issues: List[str]
    optimization_suggestions: List[str]
    buffer_time: int

@dataclass