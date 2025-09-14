
    def _update_metrics(self, operation: str) -> None:
        """Update internal metrics."""
        self._operation_count += 1
        logger.debug(f'Notification message: {operation}')
