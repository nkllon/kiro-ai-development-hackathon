from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class GetvulnerabilitycategoriesClass:
    """Auto-generated class for functions."""

    def _get_vulnerability_categories(self, findings: List[Finding]) -> List[str]:
    """Get unique vulnerability categories from findings"""
    categories = set()
    for finding in findings:
    vuln_type = finding.evidence.get('vulnerability_type', 'unknown')
    categories.add(vuln_type)
    return list(categories)

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

