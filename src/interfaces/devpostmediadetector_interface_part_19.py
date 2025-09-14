
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._files_processed = 0
        self._files_detected = 0
        self._errors = 0
        self._start_time = datetime.now()
        logger.info("Metrics reset for media detector module")