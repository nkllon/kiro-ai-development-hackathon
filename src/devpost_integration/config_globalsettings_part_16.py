from src.rm_ddd.core.health import ModuleHealth

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {'operation_count': self._operation_count, 'error_count': self._errors, 'settings_count': len(self.settings_data), 'uptime_seconds': 0}
