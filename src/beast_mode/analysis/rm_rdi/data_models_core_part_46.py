from datetime import datetime
from typing import Dict, List, Any

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
    """Compliance analysis results - READ-ONLY"""
    analysis_id: str
    timestamp: datetime
    rm_compliance_score: float
    rdi_compliance_score: float
    standards_compliance_score: float
    compliance_violations: List[ComplianceViolation]
    compliance_gaps: List[str]
    total_components_checked: int
    compliant_components: int

@dataclass(frozen=True)