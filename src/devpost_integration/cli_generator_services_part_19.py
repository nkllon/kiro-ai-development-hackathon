from src.rm_ddd.core.health import ModuleHealth

class OutputjsonClass:
    """Auto-generated class for functions."""

    def output_json(self, data: Any) -> bytes:
    """Output data as JSON"""
    try:
    json_str = json.dumps(data, indent=2, default=str)
    return json_str.encode('utf-8')
    except (TypeError, ValueError) as e:
    error_data = {'error': str(e), 'data': str(data)}
    return json.dumps(error_data).encode('utf-8')

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

