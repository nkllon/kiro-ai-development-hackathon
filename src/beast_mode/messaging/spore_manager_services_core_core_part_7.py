from src.rm_ddd.core.health import ModuleHealth

def _create_version_backup(self, spore_name: str) -> None:
    """Create a versioned backup of an existing spore"""
    try:
        if spore_name not in self._spore_cache:
            return
        current_spore = self._spore_cache[spore_name]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        version_name = f'{spore_name}_v{timestamp}'
        version_dir = self.versions_dir / version_name
        version_dir.mkdir(parents=True, exist_ok=True)
        metadata_path, content_path = self._get_spore_paths(spore_name)
        if metadata_path.exists():
            version_metadata = version_dir / 'metadata.json'
            version_metadata.write_text(metadata_path.read_text())
        if content_path.exists():
            version_content = version_dir / 'content.py'
            version_content.write_text(content_path.read_text())
        logger.info(f'Created version backup: {version_name}')
    except Exception as e:
        logger.error(f'Failed to create version backup for {spore_name}: {e}')
