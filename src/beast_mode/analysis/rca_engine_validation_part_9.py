from src.rm_ddd.core.health import ModuleHealth

def _get_pytest_subcategory(self, failure: Failure) -> str:
    """Get pytest failure subcategory"""
    if 'ImportError' in failure.error_message:
        return 'import_error'
    elif 'AssertionError' in failure.error_message:
        return 'assertion_failure'
    elif 'fixture' in failure.error_message.lower():
        return 'fixture_error'
    elif 'timeout' in failure.error_message.lower():
        return 'timeout'
    else:
        return 'general_pytest_error'

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

