from src.rm_ddd.core.health import ModuleHealth

class InitClass:
    """Auto-generated class for functions."""

    def __init__(self):
    """Initialize media detector"""
    super().__init__(module_id="media_detector", version="1.0.0")
    self.format_registry = MediaFormatRegistry()
    self.metadata_extractor = MediaMetadataExtractor()
    self._start_time = datetime.now()
    self._files_processed = 0
    self._files_detected = 0
    self._errors = 0
    register_module(self)

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

