from src.rm_ddd.core.health import ModuleHealth

    def is_media_file(self, file_path: Path) -> bool:
        """Check if file is a media file"""
        try:
            return self.format_registry.is_media_file(file_path)
        except Exception as e:
            self._errors += 1
            logger.error(f"Error checking media file {file_path}: {e}")
            return False
    