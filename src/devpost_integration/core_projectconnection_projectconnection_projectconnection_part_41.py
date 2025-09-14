from src.rm_ddd.core.health import ModuleHealth

def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'metadata_count': len(self.metadata), 'uptime_seconds': 0}
