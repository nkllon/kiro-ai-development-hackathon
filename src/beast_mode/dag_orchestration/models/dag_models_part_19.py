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
    """Task node in dependency graph."""
    task_id: str
    spec_name: str
    task_name: str
    description: str
    estimated_effort: int  # hours
    completion_status: TaskStatus
    dependencies: List[str] = field(default_factory=list)  # task IDs
    dependents: List[str] = field(default_factory=list)   # task IDs
    requirements_traced: List[str] = field(default_factory=list)
    priority: int = 1  # 1=highest, 5=lowest
    complexity: float = 1.0  # 1.0=simple, 5.0=very complex
    