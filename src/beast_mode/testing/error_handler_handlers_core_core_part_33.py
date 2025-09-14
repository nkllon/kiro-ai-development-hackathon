from src.rm_ddd.core.health import ModuleHealth

def _apply_minimal_degradation(self, reason: str) -> Dict[str, Any]:
    """Apply minimal degradation - reduce analysis depth"""
    return {'analysis_depth': 'reduced', 'pattern_matching': 'fast_only', 'timeout_reduction': '10%', 'reason': reason}

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

