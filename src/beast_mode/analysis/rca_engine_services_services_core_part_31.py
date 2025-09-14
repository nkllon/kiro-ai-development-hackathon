from src.rm_ddd.core.health import ModuleHealth

def _get_infrastructure_subcategory(self, failure: Failure) -> str:
    """Get infrastructure failure subcategory"""
    if 'PermissionError' in failure.error_message:
        return 'permission_error'
    elif 'ConnectionError' in failure.error_message:
        return 'network_error'
    elif 'resource' in failure.error_message.lower():
        return 'resource_error'
    else:
        return 'general_infrastructure_error'

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

