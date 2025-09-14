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
    """Result of systematic tool diagnosis"""
    tool_name: str
    is_healthy: bool
    issues_found: List[str]
    root_causes: List[str]
    repair_recommendations: List[str]
    confidence_score: float

@dataclass