from datetime import datetime
from typing import Dict, List, Any
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