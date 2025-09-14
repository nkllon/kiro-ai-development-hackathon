from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _create_implementation_plans(self, specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create implementation plans for generated features."""
        return [{'feature': spec['name'], 'implementation_approach': 'systematic', 'estimated_effort': '2-3 days', 'competitive_advantage': 'high'} for spec in specs]

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

