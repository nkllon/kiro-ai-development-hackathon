from src.rm_ddd.core.registry import register_module
class Agent(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
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
    """Agent: - Enhanced for compliance"""
    id: str
    name: str
    capabilities: List[str]
    max_concurrent_tasks: int = 1
    current_tasks: int = 0
    is_available: bool = True

    def __init__(self):
        register_module('Agent', self)