from src.rm_ddd.core.health import ModuleHealth

def _is_pytest_failure(self, failure: Failure) -> bool:
    """Check if failure is pytest-related"""
    return 'pytest' in failure.error_message.lower() or 'test_' in failure.component or failure.context.get('pytest_node_id') is not None or ('ImportError' in failure.error_message) or ('AssertionError' in failure.error_message)

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

