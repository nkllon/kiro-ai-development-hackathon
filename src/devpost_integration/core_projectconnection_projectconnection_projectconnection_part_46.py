from src.rm_ddd.core.health import ModuleHealth

def clear_metadata(self) -> bool:
    """Clear all metadata."""
    try:
        self.metadata.clear()
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to clear metadata: {e}')
        self._errors += 1
        return False
