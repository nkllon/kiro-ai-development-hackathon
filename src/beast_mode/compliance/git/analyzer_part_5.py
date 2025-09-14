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
    Git analysis component for identifying changes ahead of main.
    
    Analyzes git commits and file changes to support compliance checking
    by identifying the commits ahead of main and analyzing their content.
    """
