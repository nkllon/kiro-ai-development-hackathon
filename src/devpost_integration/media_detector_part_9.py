from src.rm_ddd.core.health import ModuleHealth

    def create_media_file(self, file_path: Path) -> Optional[MediaFile]:
        """Create MediaFile object from path"""
        try:
            if not self.is_media_file(file_path):
                return None
            
            # Get file info
            stat = file_path.stat()
            
            # Determine media type
            media_type = self.format_registry.get_media_type(file_path)
            
            # Extract metadata
            metadata = self.metadata_extractor.extract_metadata(file_path)
            
            return MediaFile(
                path=file_path,
                name=file_path.name,
                size=stat.st_size,
                media_type=media_type,
                metadata=metadata,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime)
            )
            
        except Exception as e:
            self._errors += 1
            logger.error(f"Error creating media file {file_path}: {e}")
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

    