
class FilematchespatternClass:
    """Auto-generated class for functions."""

    def _file_matches_pattern(self, file_path: str, pattern: str) -> bool:
    """Check if a file path matches a given pattern."""
    import fnmatch
    from src.rm_ddd.core.health import ModuleHealth

    return fnmatch.fnmatch(file_path, pattern)

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

