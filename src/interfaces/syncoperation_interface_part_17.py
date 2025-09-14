
    def reset_metrics(self) -> None:
        """Reset module metrics."""
        self._operation_count = 0
        self._errors = 0
        self.progress = 0.0
        self.start_time = None
        self.end_time = None
