
def get_preview_summary(self) -> Dict[str, Any]:
    """Get preview summary"""
    try:
        self._update_metrics('get_preview_summary')
        return {'preview_id': self.preview_id, 'content_type': self.preview_data.get('content_type', 'text'), 'title': self.preview_data.get('title', ''), 'description': self.preview_data.get('description', ''), 'thumbnail_url': self.preview_data.get('thumbnail_url', ''), 'preview_url': self.preview_data.get('preview_url', ''), 'access_count': self.preview_data.get('access_count', 0), 'status': self.preview_data.get('status', 'active'), 'generated_at': self.preview_data.get('generated_at', ''), 'expires_at': self.preview_data.get('expires_at', ''), 'is_expired': self.is_expired(), 'created_at': self.created_at, 'updated_at': self.updated_at}
    except Exception as e:
        self._logger.error(f'Failed to get preview summary: {e}')
        self._metrics['error_count'] += 1
        return {}
