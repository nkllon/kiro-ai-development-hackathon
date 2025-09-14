from src.rm_ddd.core.health import ModuleHealth

    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._operation_count = 0
        self._errors = 0
        self._start_time = datetime.now()
        logger.info("Metrics reset for multi_project_manager module")


# Export the main class
__all__ = ['MultiProjectManager']
