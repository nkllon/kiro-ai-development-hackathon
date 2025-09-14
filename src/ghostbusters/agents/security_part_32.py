from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class CalculatesecurityconfidenceClass:
    """Auto-generated class for functions."""

    def _calculate_security_confidence(self, findings: List[Finding], target_path: Path) -> float:
    """Calculate confidence score for security analysis"""
    base_confidence = 0.8
    if target_path.is_dir():
    base_confidence = 0.7
    if findings:
    avg_finding_confidence = sum((f.confidence for f in findings)) / len(findings)
    base_confidence = (base_confidence + avg_finding_confidence) / 2
    return min(1.0, max(0.0, base_confidence))

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

