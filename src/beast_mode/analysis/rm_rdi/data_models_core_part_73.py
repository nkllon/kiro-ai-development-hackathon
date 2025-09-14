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
    """Metrics analysis results - READ-ONLY"""
    analysis_id: str
    timestamp: datetime
    performance_metrics: Dict[str, float]
    quality_metrics: Dict[str, float]
    compliance_metrics: Dict[str, float]
    business_value_metrics: Dict[str, float]
    trends: List[MetricsTrend]
    collection_period: str

@dataclass