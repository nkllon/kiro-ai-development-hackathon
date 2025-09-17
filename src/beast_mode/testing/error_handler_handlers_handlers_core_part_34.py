from src.rm_ddd.core.health import ModuleHealth

def _apply_moderate_degradation(self, reason: str) -> Dict[str, Any]:
    """Apply moderate degradation - skip non-essential analysis"""
    return {'analysis_depth': 'basic', 'pattern_matching': 'disabled', 'timeout_reduction': '25%', 'comprehensive_analysis': 'disabled', 'reason': reason}

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

