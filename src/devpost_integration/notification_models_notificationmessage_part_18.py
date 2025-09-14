from src.rm_ddd.core.health import ModuleHealth

    def mark_as_failed(self) -> bool:
        """Mark message as failed."""
        try:
            self.status = 'failed'
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to mark as failed: {e}')
            self._errors += 1
            return False
