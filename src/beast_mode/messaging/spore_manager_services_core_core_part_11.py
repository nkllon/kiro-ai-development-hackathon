from src.rm_ddd.core.health import ModuleHealth

def update_spore_stats(self, spore_name: str, success: bool) -> None:
    """
        Update spore usage statistics
        
        Args:
            spore_name: Name of the spore
            success: Whether the spore execution was successful
        """
    try:
        if spore_name not in self._spore_cache:
            return
        spore = self._spore_cache[spore_name]
        metadata = spore.metadata
        metadata.usage_count += 1
        if metadata.usage_count == 1:
            metadata.success_rate = 1.0 if success else 0.0
        else:
            total_successes = metadata.success_rate * (metadata.usage_count - 1)
            if success:
                total_successes += 1
            metadata.success_rate = total_successes / metadata.usage_count
        metadata_path, _ = self._get_spore_paths(spore_name)
        with open(metadata_path, 'w') as f:
            json.dump(metadata.model_dump(), f, indent=2, default=str)
    except Exception as e:
        logger.error(f'Failed to update stats for {spore_name}: {e}')
