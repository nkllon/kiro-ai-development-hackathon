
def is_expired(self) -> bool:
    """Check if preview is expired"""
    try:
        self._update_metrics('is_expired')
        if not self.preview_data.get('expires_at'):
            return False
        expires_at = datetime.fromisoformat(self.preview_data['expires_at'])
        return datetime.now() > expires_at
    except Exception as e:
        self._logger.error(f'Failed to check expiration: {e}')
        self._metrics['error_count'] += 1
        return False
