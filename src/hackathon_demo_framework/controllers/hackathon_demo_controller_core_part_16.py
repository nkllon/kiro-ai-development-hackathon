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
    """Represents a demo session for a judge"""
    session_id: str
    judge_id: str
    start_time: datetime
    current_phase: DemoPhase
    progress: float
    interactions: List[Dict[str, Any]]
    systematic_score: float
    learning_patterns: List[Dict[str, Any]]

@dataclass