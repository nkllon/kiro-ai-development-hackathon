from src.rm_ddd.core.health import ModuleHealth

    def _extract_method_docstring(self, method: callable) -> str:
        """Extract docstring from method"""
        try:
            return method.__doc__ or f'Execute {method.__name__} operation'
        except:
            return f'Execute {method.__name__} operation'

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

