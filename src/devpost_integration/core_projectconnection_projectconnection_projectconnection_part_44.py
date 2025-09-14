from src.rm_ddd.core.health import ModuleHealth

class GetmetadataClass:
    """Auto-generated class for functions."""

    def get_metadata(self, key: str=None) -> Any:
    """Get metadata value or all metadata."""
    try:
    if key is None:
    return self.metadata
    return self.metadata.get(key)
    except Exception as e:
    logger.error(f'Failed to get metadata: {e}')
    self._errors += 1
    return None

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

