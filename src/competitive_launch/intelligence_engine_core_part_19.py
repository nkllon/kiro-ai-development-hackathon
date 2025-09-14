from src.rm_ddd.core.health import ModuleHealth

def _calculate_differentiation_advantage(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate competitive advantage of differentiation strategy."""
    return {'advantage_score': 0.75, 'differentiation_strength': 'high', 'market_positioning': 'superior'}

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

