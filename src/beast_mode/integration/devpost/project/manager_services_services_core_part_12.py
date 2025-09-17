from src.rm_ddd.core.health import ModuleHealth

def _find_media_files(self) -> List[Path]:
    """Find media files in the project."""
    media_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.mp4', '.mov', '.avi', '.webm'}
    media_files = []
    media_dirs = ['media', 'images', 'screenshots', 'assets', 'docs/images']
    for dir_name in media_dirs:
        media_dir = self.project_root / dir_name
        if media_dir.exists():
            for file_path in media_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in media_extensions:
                    media_files.append(file_path)
    for pattern in ['screenshot*', 'demo*', 'preview*']:
        for file_path in self.project_root.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in media_extensions:
                media_files.append(file_path)
    return media_files

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

