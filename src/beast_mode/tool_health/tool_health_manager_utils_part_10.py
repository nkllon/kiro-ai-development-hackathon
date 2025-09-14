
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
    """Result of systematic tool repair"""
    tool_name: str
    repair_successful: bool
    repairs_applied: List[str]
    validation_passed: bool
    time_to_repair: timedelta
    prevention_pattern: Optional[str] = None
