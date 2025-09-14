from src.rm_ddd.core.health import ModuleHealth

def get_sync_status(self) -> Dict[str, Any]:
    """Get current sync status."""
    return {'operation_id': self.operation_id, 'status': self.status, 'progress': self.progress, 'start_time': self.start_time.isoformat() if self.start_time else None, 'end_time': self.end_time.isoformat() if self.end_time else None, 'error_message': self.error_message, 'operation_count': self._operation_count, 'error_count': self._errors}
