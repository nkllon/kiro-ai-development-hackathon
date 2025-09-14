from src.rm_ddd.core.health import ModuleHealth

    def add_processed_record(self) -> None:
        """Increment processed records count."""
        try:
            self.records_processed += 1
            self._operation_count += 1
        except Exception as e:
            logger.error(f'Failed to add processed record: {e}')
            self._errors += 1
