from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class GetstatusreportClass:
    """Auto-generated class for functions."""

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
    """Comprehensive analysis result - IMMUTABLE and SAFE"""
    analysis_id: str
    timestamp: datetime
    analysis_types: List[str]
    status: AnalysisStatus
    architecture_analysis: Optional[ArchitectureAnalysis] = None
    quality_analysis: Optional[QualityReport] = None
    compliance_analysis: Optional[ComplianceReport] = None
    technical_debt_analysis: Optional[TechnicalDebtReport] = None
    performance_analysis: Optional[PerformanceReport] = None
    metrics_analysis: Optional[MetricsReport] = None
    recommendations: List[Recommendation] = field(default_factory=list)
    overall_health_score: float = 0.0
    safety_metrics: Optional[SafetyMetrics] = None
    findings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    confidence: float = 1.0
    operator_notes: List[str] = field(default_factory=list)
    safety_validated: bool = True
    can_be_safely_ignored: bool = True
    emergency_shutdown_available: bool = True

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

