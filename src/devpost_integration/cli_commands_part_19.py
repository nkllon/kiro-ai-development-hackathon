from src.rm_ddd.core.health import ModuleHealth

    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()