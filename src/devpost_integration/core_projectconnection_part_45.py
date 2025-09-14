
def update_metadata(self, updates: Dict[str, Any]) -> bool:
    """Update multiple metadata fields."""
    try:
        self.metadata.update(updates)
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to update metadata: {e}')
        self._errors += 1
        return False
