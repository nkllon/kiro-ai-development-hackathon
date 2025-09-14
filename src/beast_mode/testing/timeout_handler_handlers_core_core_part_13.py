from src.rm_ddd.core.health import ModuleHealth

def _cleanup_operation_callbacks(self, operation_id: str) -> None:
    """Clean up operation callbacks"""
    if operation_id in self.operation_callbacks:
        del self.operation_callbacks[operation_id]

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

