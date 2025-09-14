
def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'success': self.success, 'records_processed': self.records_processed, 'records_failed': self.records_failed, 'sync_time': self.sync_time.isoformat(), 'success_rate': (self.records_processed - self.records_failed) / max(1, self.records_processed)}
