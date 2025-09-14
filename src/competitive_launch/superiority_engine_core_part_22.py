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
    """ROI calculation for systematic approach."""
    investment_cost: float
    systematic_benefits: float
    adhoc_benefits: float
    net_benefit: float
    roi_percentage: float
    payback_period_months: float
    risk_adjusted_roi: float
    calculation_date: datetime = field(default_factory=datetime.now)

@dataclass