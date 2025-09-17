from src.rm_ddd.core.health import ModuleHealth

def _is_make_failure(self, failure: Failure) -> bool:
    """Check if failure is make-related"""
    return 'make' in failure.component.lower() or 'Makefile' in failure.error_message or 'No rule to make target' in failure.error_message or ('missing separator' in failure.error_message)

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

