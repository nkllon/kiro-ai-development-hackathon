
def set_thumbnail(self, thumbnail_url: str) -> bool:
    """Set preview thumbnail URL"""
    try:
        self._update_metrics('set_thumbnail')
        self.preview_data['thumbnail_url'] = thumbnail_url
        self.updated_at = datetime.now()
        self._logger.info(f'Thumbnail set for preview {self.preview_id}: {thumbnail_url}')
        return True
    except Exception as e:
        self._logger.error(f'Failed to set thumbnail: {e}')
        self._metrics['error_count'] += 1
        return False
