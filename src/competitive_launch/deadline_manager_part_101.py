from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _identify_scope_reduction_opportunities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify opportunities for scope reduction."""
    opportunities = []
    if analysis['behind_schedule']:
        opportunities.extend([{'type': 'optional_features', 'time_saved': 2, 'competitive_impact': 0.1, 'priority': 'high'}, {'type': 'nice_to_have_improvements', 'time_saved': 1.5, 'competitive_impact': 0.05, 'priority': 'high'}])
    return opportunities

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

