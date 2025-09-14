from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _prioritize_by_competitive_impact(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prioritize scope reduction opportunities by competitive impact."""
    return sorted(opportunities, key=lambda x: x['competitive_impact'])

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

