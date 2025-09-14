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
    """Specification node in dependency graph."""
    spec_name: str
    spec_path: str
    completion_percentage: float
    task_count: int
    completed_tasks: int
    dependencies: List[str] = field(default_factory=list)  # spec names
    dependents: List[str] = field(default_factory=list)   # spec names
    layer: int = 0  # dependency layer (0 = no dependencies)
    