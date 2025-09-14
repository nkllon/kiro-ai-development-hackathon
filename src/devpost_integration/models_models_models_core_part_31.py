
def increment_access_count(self) -> bool:
    """Increment preview access count"""
    try:
        self._update_metrics('increment_access_count')
        self.preview_data['access_count'] = self.preview_data.get('access_count', 0) + 1
        self.updated_at = datetime.now()
        self._logger.info(f"Access count incremented for preview {self.preview_id}: {self.preview_data['access_count']}")
        return True
    except Exception as e:
        self._logger.error(f'Failed to increment access count: {e}')
        self._metrics['error_count'] += 1
        return False
