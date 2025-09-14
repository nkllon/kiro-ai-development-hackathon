from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _configure_htap(self, resources: TiDBResources) -> Dict[str, Any]:
    """Configure HTAP (Hybrid Transactional/Analytical Processing)."""
    return {'success': True, 'tikv_nodes': resources.nodes, 'tidb_nodes': max(1, resources.nodes // 2), 'pd_nodes': 3}

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

