
def _update_metrics(self, operation: str) -> None:
    """Update performance metrics"""
    self._metrics['operations_count'] += 1
    self._metrics['last_operation_time'] = datetime.now()
    total_ops = self._metrics['operations_count']
    errors = self._metrics['error_count']
    self._metrics['success_rate'] = (total_ops - errors) / total_ops if total_ops > 0 else 1.0
