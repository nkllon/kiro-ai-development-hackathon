from src.rm_ddd.core.registry import register_module
class PerformanceReport(ReflectiveModule):
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
    """Performance analysis results - READ-ONLY"""
    analysis_id: str
    timestamp: datetime
    overall_performance_score: float
    rm_performance_metrics: List[PerformanceMetric]
    rdi_performance_metrics: List[PerformanceMetric]
    bottlenecks_identified: List[str]
    optimization_opportunities: List[str]
    resource_usage: Dict[str, float]

@dataclass(frozen=True)
    def __init__(self):
        register_module('PerformanceReport', self)