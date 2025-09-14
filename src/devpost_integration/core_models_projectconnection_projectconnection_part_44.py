
def get_metadata(self, key: str=None) -> Any:
    """Get metadata value or all metadata."""
    try:
        if key is None:
            return self.metadata
        return self.metadata.get(key)
    except Exception as e:
        logger.error(f'Failed to get metadata: {e}')
        self._errors += 1
        return None
