from src.rm_ddd.core.health import ModuleHealth

class InitClass:
    """Auto-generated class for functions."""

    def __init__(self, spore_directory: str='spores'):
    """
    Initialize SporeManager

    Args:
    spore_directory: Directory to store spores
    """
    self.spore_directory = Path(spore_directory)
    self.spore_directory.mkdir(parents=True, exist_ok=True)
    self.metadata_dir = self.spore_directory / 'metadata'
    self.content_dir = self.spore_directory / 'content'
    self.versions_dir = self.spore_directory / 'versions'
    for directory in [self.metadata_dir, self.content_dir, self.versions_dir]:
    directory.mkdir(parents=True, exist_ok=True)
    self._spore_cache: Dict[str, SporeContent] = {}
    self._load_existing_spores()

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

