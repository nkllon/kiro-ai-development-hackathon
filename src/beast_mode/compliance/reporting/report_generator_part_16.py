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
    """Comprehensive compliance report with all analysis results."""
    report_id: str
    generation_timestamp: datetime
    analysis_result: ComplianceAnalysisResult
    executive_summary: str
    detailed_findings: Dict[str, Any]
    remediation_plan: List[RemediationStep]
    phase3_readiness_assessment: Dict[str, Any]
    formatted_report: str

@dataclass