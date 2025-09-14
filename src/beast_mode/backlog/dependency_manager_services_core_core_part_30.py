
def _is_performance_healthy(self) -> bool:
    """Check if performance is within acceptable limits"""
    avg_time = self._get_avg_operation_time()
    return avg_time <= 500.0
