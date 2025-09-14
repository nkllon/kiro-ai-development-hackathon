from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _estimate_competitive_advantage(self, specs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Estimate competitive advantage of generated features."""
    return {'advantage_score': 0.75, 'estimated_days': 5, 'differentiation_strength': 'high'}

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

