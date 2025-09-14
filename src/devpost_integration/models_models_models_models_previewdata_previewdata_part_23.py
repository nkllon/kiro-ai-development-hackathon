from src.rm_ddd.core.health import ModuleHealth

    def set_expiration(self, expires_at: datetime) -> bool:
        """Set preview expiration time"""
        try:
            self._update_metrics('set_expiration')
            self.preview_data['expires_at'] = expires_at.isoformat()
            self.updated_at = datetime.now()
            self._logger.info(f'Expiration set for preview {self.preview_id}: {expires_at}')
            return True
        except Exception as e:
            self._logger.error(f'Failed to set expiration: {e}')
            self._metrics['error_count'] += 1
            return False
