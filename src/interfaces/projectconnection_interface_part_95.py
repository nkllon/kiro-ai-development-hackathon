from src.rm_ddd.core.health import ModuleHealth

def complete_sync(self, success: bool=True) -> bool:
    """Complete synchronization operation."""
    try:
        self.end_time = datetime.now()
        self.status = 'completed' if success else 'failed'
        self.progress = 1.0 if success else self.progress
        self._update_metrics('complete_sync')
        return True
    except Exception as e:
        logger.error(f'Failed to complete sync: {e}')
        self._errors += 1
        return False
