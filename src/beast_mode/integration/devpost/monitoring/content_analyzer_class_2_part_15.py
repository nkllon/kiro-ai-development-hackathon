from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _get_media_category(self, file_path: Path) -> str:
        """Get media file category."""
        suffix = file_path.suffix.lower()
        if suffix in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}:
            return 'image'
        elif suffix in {'.mp4', '.mov', '.avi', '.webm', '.mkv'}:
            return 'video'
        elif suffix in {'.pdf', '.doc', '.docx'}:
            return 'document'
        else:
            return 'other'

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

