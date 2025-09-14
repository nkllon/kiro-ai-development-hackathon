from src.rm_ddd.core.health import ModuleHealth

class GetsporepathsClass:
    """Auto-generated class for functions."""

    def _get_spore_paths(self, spore_name: str) -> Tuple[Path, Path]:
    """Get metadata and content file paths for a spore"""
    metadata_path = self.metadata_dir / f'{spore_name}.json'
    content_path = self.content_dir / f'{spore_name}.py'
    return (metadata_path, content_path)

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

