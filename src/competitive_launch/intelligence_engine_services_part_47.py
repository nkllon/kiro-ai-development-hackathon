from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _calculate_threat_level(self, insights: List[str]) -> str:
        """Calculate overall competitive threat level."""
        if any(('immediate response needed' in insight for insight in insights)):
            return 'high'
        elif len(insights) > 2:
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

