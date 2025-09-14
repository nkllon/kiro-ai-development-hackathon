from src.rm_ddd.core.health import ModuleHealth

    def update_metadata(self, updates: Dict[str, Any]) -> bool:
        """Update multiple metadata values"""
        try:
            self._update_metrics('update_metadata')
            self.metadata.update(updates)
            self.updated_at = datetime.now()
            self._metrics['metadata_updates'] += len(updates)
            self._logger.info(f'Metadata updated with {len(updates)} values')
            return True
        except Exception as e:
            self._logger.error(f'Failed to update metadata: {e}')
            self._metrics['error_count'] += 1
            return False
