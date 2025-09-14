class BeastReadinessStatus(Enum, ReflectiveModule):
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
    """Status levels for beast-readiness of backlog items"""
    DRAFT = "draft"
    MPM_REVIEW = "mpm_review"
    GHOSTBUSTERS_VALIDATION = "ghostbusters_validation"
    BEAST_READY = "beast_ready"
    IN_EXECUTION = "in_execution"
    COMPLETED = "completed"
    BLOCKED = "blocked"

