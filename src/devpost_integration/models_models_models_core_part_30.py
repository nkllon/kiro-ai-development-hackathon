
def set_preview_url(self, preview_url: str) -> bool:
    """Set preview URL"""
    try:
        self._update_metrics('set_preview_url')
        self.preview_data['preview_url'] = preview_url
        self.updated_at = datetime.now()
        self._logger.info(f'Preview URL set for {self.preview_id}: {preview_url}')
        return True
    except Exception as e:
        self._logger.error(f'Failed to set preview URL: {e}')
        self._metrics['error_count'] += 1
        return False
