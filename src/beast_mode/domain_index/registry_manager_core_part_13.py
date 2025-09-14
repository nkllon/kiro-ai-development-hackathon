from src.rm_ddd.core.health import ModuleHealth

class ReloadregistryClass:
    """Auto-generated class for functions."""

    def reload_registry(self) -> bool:
    """Reload registry from file"""
    self.logger.info('Reloading domain registry')
    self._registry_loaded = False
    self._clear_cache()
    return self.load_registry()

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

