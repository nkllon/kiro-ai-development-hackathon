from src.rm_ddd.core.health import ModuleHealth

class ResetglobalregistryClass:
    """Auto-generated class for functions."""

    def reset_global_registry():
    """Reset the global registry (primarily for testing)."""
    global _global_registry
    with _registry_lock:
    if _global_registry:
    pass
    _global_registry = GlobalRegistry()


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

    @property