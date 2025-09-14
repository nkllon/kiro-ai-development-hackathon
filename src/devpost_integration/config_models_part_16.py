
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {'operation_count': self._operation_count, 'error_count': self._errors, 'config_keys': len(self.config_data), 'uptime_seconds': 0}
