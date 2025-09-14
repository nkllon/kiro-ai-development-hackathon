from src.rm_ddd.core.registry import register_module
class ComplianceReport(ReflectiveModule):
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
    def __init__(self):
        register_module('ComplianceReport', self)