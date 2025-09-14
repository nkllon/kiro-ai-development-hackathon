from src.rm_ddd.core.health import ModuleHealth

def get_global_registry() -> GlobalRegistry:
    """
    Get the global registry instance.
    
    Returns:
        The singleton GlobalRegistry instance
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = GlobalRegistry()
        return _global_registry

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

