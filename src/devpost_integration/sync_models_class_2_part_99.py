from src.rm_ddd.core.health import ModuleHealth

def update_file_path(self, new_path: str) -> bool:
    """Update file path."""
    try:
        self.file_path = new_path
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to update file path: {e}')
        self._errors += 1
        return False
