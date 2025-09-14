from src.rm_ddd.core.health import ModuleHealth

def set_metadata(self, key: str, value: Any) -> bool:
    """Set metadata value."""
    try:
        self.metadata[key] = value
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to set metadata: {e}')
        self._errors += 1
        return False
