from src.rm_ddd.core.health import ModuleHealth

class IsmediafileClass:
    """Auto-generated class for functions."""

    def is_media_file(self, file_path: Path) -> bool:
    """Check if file is a media file"""
    try:
    return self.format_registry.is_media_file(file_path)
    except Exception as e:
    self._errors += 1
    logger.error(f"Error checking media file {file_path}: {e}")
    return False

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

