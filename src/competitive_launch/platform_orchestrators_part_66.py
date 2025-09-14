from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _analyze_market_gap(self, market_gap: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market gap for feature generation."""
        return {'gap_size': 'large', 'differentiation_factors': ['systematic_approach', 'fmh_principles', 'requirements_driven'], 'competitive_opportunity': 'high'}

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

