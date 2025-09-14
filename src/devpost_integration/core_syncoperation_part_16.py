from src.rm_ddd.core.health import ModuleHealth

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {'operation_count': self._operation_count, 'error_count': self._errors, 'current_progress': self.progress, 'status': self.status, 'uptime_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0}
