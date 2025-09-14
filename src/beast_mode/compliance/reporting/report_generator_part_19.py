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
    """High-level compliance summary for quick assessment."""
    overall_score: float
    total_issues: int
    critical_issues: int
    high_priority_issues: int
    phase3_ready: bool
    key_blockers: List[str]
    next_actions: List[str]
