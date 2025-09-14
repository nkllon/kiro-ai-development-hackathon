
def _calculate_health_score(self) -> float:
    """Calculate health score based on metrics"""
    if self._metrics['operations_count'] == 0:
        return 1.0
    success_rate = self._metrics['success_rate']
    error_penalty = min(self._metrics['error_count'] * 0.1, 0.5)
    return max(0.0, success_rate - error_penalty)
