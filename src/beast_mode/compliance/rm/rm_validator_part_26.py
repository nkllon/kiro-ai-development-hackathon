from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class GeneratereportClass:
    """Auto-generated class for functions."""

    def generate_report(self) -> Dict[str, Any]:
    """Generate compliance report"""
    if not self.compliance_results:
    return {"message": "No compliance data available"}

    total_interfaces = len(self.compliance_results)
    high_compliance = len([r for r in self.compliance_results.values() if r.level == ComplianceLevel.HIGH])
    medium_compliance = len([r for r in self.compliance_results.values() if r.level == ComplianceLevel.MEDIUM])
    low_compliance = len([r for r in self.compliance_results.values() if r.level == ComplianceLevel.LOW])
    critical_compliance = len([r for r in self.compliance_results.values() if r.level == ComplianceLevel.CRITICAL])

    avg_score = sum(r.compliance_score for r in self.compliance_results.values()) / total_interfaces

    return {
    "total_interfaces": total_interfaces,
    "average_compliance_score": round(avg_score, 2),
    "compliance_distribution": {
    "high": high_compliance,
    "medium": medium_compliance,
    "low": low_compliance,
    "critical": critical_compliance
    },
    "results": {
    name: {
    "score": result.compliance_score,
    "level": result.level.value,
    "issues": result.issues,
    "recommendations": result.recommendations
    }
    for name, result in self.compliance_results.items()
    }
    }

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

