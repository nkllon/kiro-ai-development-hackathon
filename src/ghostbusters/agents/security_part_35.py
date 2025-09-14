from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _calculate_risk_level(self, findings: List[Finding]) -> str:
        """Calculate overall risk level based on findings"""
        if not findings:
            return 'low'
        critical_count = sum((1 for f in findings if f.severity == Severity.CRITICAL))
        high_count = sum((1 for f in findings if f.severity == Severity.HIGH))
        if critical_count > 0:
            return 'critical'
        elif high_count > 2:
            return 'high'
        elif high_count > 0:
            return 'medium'
        else:
            return 'low'

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

