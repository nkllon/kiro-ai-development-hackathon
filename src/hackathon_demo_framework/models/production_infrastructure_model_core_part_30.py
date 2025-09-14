
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
    """Result of cost optimization analysis"""
    optimization_id: str
    current_cost: float
    optimized_cost: float
    savings_percentage: float
    optimization_recommendations: List[str]
    implementation_plan: Dict[str, Any]
    created_at: datetime

@dataclass