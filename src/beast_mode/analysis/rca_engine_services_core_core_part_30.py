from src.rm_ddd.core.health import ModuleHealth

def _get_make_subcategory(self, failure: Failure) -> str:
    """Get make failure subcategory"""
    if 'No rule to make target' in failure.error_message:
        return 'missing_target'
    elif 'missing separator' in failure.error_message:
        return 'syntax_error'
    elif 'No such file' in failure.error_message:
        return 'missing_file'
    else:
        return 'general_make_error'

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

