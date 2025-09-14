from src.rm_ddd.core.registry import register_module
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
    """Result of multi-agent collaboration"""
    collaboration_id: str
    task_description: str
    participating_agents: List[str]
    coordination_events: List[Dict[str, Any]]
    conflicts_resolved: List[Dict[str, Any]]
    human_amplification: Dict[str, Any]
    final_output: Dict[str, Any]
    created_at: datetime
