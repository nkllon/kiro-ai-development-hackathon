
def delete_spore(self, spore_name: str) -> bool:
    """
        Delete a spore and its versions
        
        Args:
            spore_name: Name of the spore to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
    try:
        if spore_name in self._spore_cache:
            del self._spore_cache[spore_name]
        metadata_path, content_path = self._get_spore_paths(spore_name)
        if metadata_path.exists():
            metadata_path.unlink()
        if content_path.exists():
            content_path.unlink()
        version_pattern = f'{spore_name}_v*'
        for version_dir in self.versions_dir.glob(version_pattern):
            if version_dir.is_dir():
                for file in version_dir.iterdir():
                    file.unlink()
                version_dir.rmdir()
        logger.info(f'Successfully deleted spore: {spore_name}')
        return True
    except Exception as e:
        logger.error(f'Failed to delete spore {spore_name}: {e}')
        return False
