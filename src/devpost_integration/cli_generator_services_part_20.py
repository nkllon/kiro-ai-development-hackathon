from src.rm_ddd.core.health import ModuleHealth

class OutputtextClass:
    """Auto-generated class for functions."""

    def output_text(self, data: Any) -> bytes:
    """Output data as text"""
    if isinstance(data, list):
    return '\n'.join((str(item) for item in data)).encode('utf-8')
    else:
    return str(data).encode('utf-8')

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

