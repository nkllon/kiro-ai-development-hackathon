from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def stateless_init(self, *args, **kwargs):
    self._initializing = True
    original_init(self, *args, **kwargs)
    del self._initializing

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

