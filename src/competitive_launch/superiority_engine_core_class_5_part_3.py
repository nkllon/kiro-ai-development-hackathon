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
    """Evidence package for marketing/sales."""
    package_id: str
    title: str
    metrics: List[SuperiorityMetric]
    roi_calculation: ROICalculation
    competitive_advantages: List[str]
    customer_testimonials: List[str]
    case_studies: List[str]
    generated_at: datetime = field(default_factory=datetime.now)
