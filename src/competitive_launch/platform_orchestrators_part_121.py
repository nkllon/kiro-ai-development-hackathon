from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _analyze_scaling_demand(self, demand: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze current demand to determine scaling needs."""
    return {'scale_up': demand.get('cpu_usage', 0) > 0.8, 'scale_down': demand.get('cpu_usage', 0) < 0.3, 'target_replicas': max(1, int(demand.get('current_replicas', 1) * 1.5))}

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

