from src.rm_ddd.core.health import ModuleHealth

def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'connected': self.connected, 'connection_duration': (datetime.now() - self.connection_time).total_seconds() if self.connection_time else 0}
