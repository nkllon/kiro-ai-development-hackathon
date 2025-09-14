from src.rm_ddd.core.health import ModuleHealth

    def add_failed_record(self) -> None:
        """Increment failed records count."""
        try:
            self.records_failed += 1
            self._operation_count += 1
        except Exception as e:
            logger.error(f'Failed to add failed record: {e}')
            self._errors += 1
