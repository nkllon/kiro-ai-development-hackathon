from src.rm_ddd.core.health import ModuleHealth

class IsinfrastructurefailureClass:
    """Auto-generated class for functions."""

    def _is_infrastructure_failure(self, failure: Failure) -> bool:
    """Check if failure is infrastructure-related"""
    return 'PermissionError' in failure.error_message or 'ConnectionError' in failure.error_message or 'system' in failure.component.lower() or ('environment' in failure.error_message.lower())

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

