from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _determine_competitive_position(self, advantage: float) -> str:
        """Determine competitive position based on advantage score."""
        if advantage >= 0.8:
            return 'market_leader'
        elif advantage >= 0.6:
            return 'strong_competitor'
        elif advantage >= 0.4:
            return 'competitive'
        else:
            return 'behind_competitors'

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

