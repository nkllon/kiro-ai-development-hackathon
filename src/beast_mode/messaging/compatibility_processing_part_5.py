from src.rm_ddd.core.health import ModuleHealth

class Convertfromv11Class:
    """Auto-generated class for functions."""

    def _convert_from_v1_1(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert from V1.1 format"""
    converted = message_data.copy()
    if 'request_id' in converted and 'correlation_id' not in converted:
    converted['correlation_id'] = converted.pop('request_id')
    return converted

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

