
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
    """Result of comparing systematic vs ad-hoc approaches"""
    comparison_id: str
    systematic_approach: Approach
    adhoc_approach: Approach
    improvement_factor: float
    statistical_significance: float
    confidence_interval: Tuple[float, float]
    evidence_package: Dict[str, Any]
    created_at: datetime

@dataclass