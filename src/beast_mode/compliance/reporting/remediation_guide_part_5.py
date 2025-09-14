
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
    """Categories of remediation actions."""
    IMMEDIATE_FIX = 'immediate_fix'
    REFACTORING = 'refactoring'
    TESTING = 'testing'
    DOCUMENTATION = 'documentation'
    ARCHITECTURE = 'architecture'
    PROCESS = 'process'

@dataclass