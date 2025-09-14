from src.rm_ddd.core.health import ModuleHealth

class DeterminesystematiclocationClass:
    """Auto-generated class for functions."""

    def _determine_systematic_location(self, file_path: Path, category: FileCategory) -> str:
    """Determine systematic location for file based on category"""
    location_mapping = {FileCategory.SYSTEMATIC_DOCUMENT: 'docs/systematic/', FileCategory.DEVELOPMENT_ARTIFACT: 'archive/development-artifacts/', FileCategory.TEST_FILE: 'tests/', FileCategory.SCRIPT: 'scripts/', FileCategory.RESEARCH: 'archive/research/', FileCategory.CONFIGURATION: 'config/', FileCategory.MEDIA: 'archive/media/', FileCategory.TEMPORARY: 'DELETE', FileCategory.UNKNOWN: 'archive/uncategorized/'}
    return location_mapping.get(category, 'archive/uncategorized/')

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

