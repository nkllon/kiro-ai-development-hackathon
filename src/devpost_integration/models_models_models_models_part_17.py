from src.rm_ddd.core.health import ModuleHealth

    def set_metadata(self, key: str, value: Any) -> bool:
        """Set metadata value"""
        try:
            self._update_metrics('set_metadata')
            self.metadata[key] = value
            self.updated_at = datetime.now()
            self._metrics['metadata_updates'] += 1
            self._logger.info(f'Metadata set: {key}')
            return True
        except Exception as e:
            self._logger.error(f'Failed to set metadata: {e}')
            self._metrics['error_count'] += 1
            return False
