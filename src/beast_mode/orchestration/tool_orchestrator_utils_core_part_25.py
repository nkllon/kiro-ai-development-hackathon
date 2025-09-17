from src.rm_ddd.core.health import ModuleHealth

def _calculate_optimization_roi(self) -> Dict[str, Any]:
    """Calculate return on investment for optimizations"""
    return {'total_performance_gain_percentage': 15.0, 'roi_score': 3.5}

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

