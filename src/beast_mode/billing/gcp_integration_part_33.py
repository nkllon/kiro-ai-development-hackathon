from src.rm_ddd.core.health import ModuleHealth

def get_configuration(self) -> Dict[str, Any]:
    """Get current configuration for RM pattern"""
    return {'integration_mode': self.integration_mode, 'cache_duration_minutes': self.cache_duration.total_seconds() / 60, 'config_keys': list(self.config.keys())}

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

