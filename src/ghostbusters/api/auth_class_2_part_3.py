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
    """
    Manages authentication and authorization for Ghostbusters API.
    
    Provides token-based authentication with configurable security policies.
    """
    