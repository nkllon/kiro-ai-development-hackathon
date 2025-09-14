from src.rm_ddd.core.health import ModuleHealth

def clear_metadata(self) -> bool:
    """Clear all metadata"""
    try:
        self._update_metrics('clear_metadata')
        self.metadata.clear()
        self.updated_at = datetime.now()
        self._logger.info('Metadata cleared successfully')
        return True
    except Exception as e:
        self._logger.error(f'Failed to clear metadata: {e}')
        self._metrics['error_count'] += 1
        return False
