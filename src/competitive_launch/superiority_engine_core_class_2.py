from src.rm_ddd.core.registry import register_module
class MetricType(Enum, ReflectiveModule):
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
    """Types of superiority metrics."""
    DEVELOPMENT_VELOCITY = 'development_velocity'
    QUALITY_IMPROVEMENT = 'quality_improvement'
    TECHNICAL_DEBT_REDUCTION = 'technical_debt_reduction'
    COST_EFFICIENCY = 'cost_efficiency'
    RISK_MITIGATION = 'risk_mitigation'
    CUSTOMER_SATISFACTION = 'customer_satisfaction'
    TIME_TO_MARKET = 'time_to_market'
    MAINTENANCE_EFFICIENCY = 'maintenance_efficiency'

@dataclass
    def __init__(self):
        register_module('MetricType', self)