from src.rm_ddd.core.registry import register_module

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
    Utility class for normalizing and handling path operations consistently.
    
    This class provides static methods to handle common path operations that can
    cause issues when mixing absolute and relative paths.
    """

    @staticmethod