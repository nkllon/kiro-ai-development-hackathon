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
    """Refactoring opportunity details"""
    opportunity_id: str
    type: str
    description: str
    files_affected: List[str]
    effort_estimate: int
    impact_score: float

@dataclass(frozen=True)