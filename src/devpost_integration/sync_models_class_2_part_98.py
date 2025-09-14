from src.rm_ddd.core.health import ModuleHealth

class GeteventdetailsClass:
    """Auto-generated class for functions."""

    def get_event_details(self) -> Dict[str, Any]:
    """Get detailed event information."""
    return {'file_path': self.file_path, 'change_type': self.change_type.value if hasattr(self.change_type, 'value') else str(self.change_type), 'timestamp': self.timestamp.isoformat(), 'file_size': self.file_size, 'checksum': self.checksum}

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

