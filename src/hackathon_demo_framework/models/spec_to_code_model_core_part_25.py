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
    """Result of spec-to-code transformation"""
    spec_id: str
    generated_code: str
    quality_level: QualityLevel
    systematic_score: float
    test_coverage: float
    security_validation: bool
    performance_metrics: Dict[str, Any]
    learning_patterns: List[LearningPattern]
    created_at: datetime
