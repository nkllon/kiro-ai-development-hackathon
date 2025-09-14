from src.rm_ddd.core.health import ModuleHealth

    def detect_media_files(self, directory: Path, recursive: bool = True) -> List[MediaFile]:
        """Detect media files in directory"""
        try:
            media_files = []
            
            if not directory.exists():
                logger.warning(f"Directory does not exist: {directory}")
                return media_files
            
            # Get file pattern
            pattern = "**/*" if recursive else "*"
            
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    self._files_processed += 1
                    
                    # Check if file is media
                    if self.is_media_file(file_path):
                        media_file = self.create_media_file(file_path)
                        if media_file:
                            media_files.append(media_file)
                            self._files_detected += 1
            
            logger.info(f"Detected {len(media_files)} media files in {directory}")
            return media_files
            
        except Exception as e:
            self._errors += 1
            logger.error(f"Error detecting media files: {e}")
            return []

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

    