from src.rm_ddd.core.health import ModuleHealth

def _apply_emergency_degradation(self, reason: str) -> Dict[str, Any]:
    """Apply emergency degradation - fallback mode only"""
    return {'analysis_depth': 'none', 'fallback_mode': 'enabled', 'all_advanced_features': 'disabled', 'basic_reporting_only': True, 'reason': reason}

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

