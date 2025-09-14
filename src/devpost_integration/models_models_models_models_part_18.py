from src.rm_ddd.core.health import ModuleHealth

    def get_metadata(self, key: str=None) -> Any:
        """Get metadata value or all metadata"""
        try:
            self._update_metrics('get_metadata')
            if key is None:
                return self.metadata.copy()
            return self.metadata.get(key)
        except Exception as e:
            self._logger.error(f'Failed to get metadata: {e}')
            self._metrics['error_count'] += 1
            return None
