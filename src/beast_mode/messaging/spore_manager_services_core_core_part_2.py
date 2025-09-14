from src.rm_ddd.core.health import ModuleHealth

def _load_existing_spores(self) -> None:
    """Load existing spores from disk into cache"""
    try:
        for metadata_file in self.metadata_dir.glob('*.json'):
            spore_name = metadata_file.stem
            try:
                spore = self.load_spore(spore_name)
                if spore:
                    self._spore_cache[spore_name] = SporeContent(**spore)
            except Exception as e:
                logger.warning(f'Failed to load spore {spore_name}: {e}')
    except Exception as e:
        logger.error(f'Failed to load existing spores: {e}')
