
def get_health_indicators(self) -> Dict[str, Any]:
    """Detailed health metrics for operational visibility"""
    return {'detection_capability': {'status': 'healthy' if not self._degradation_active else 'degraded', 'runs_monitored': self.total_test_runs_monitored, 'failures_detected': self.total_failures_detected}, 'parsing_performance': {'status': 'healthy' if self.parsing_success_rate > 0.8 else 'degraded', 'success_rate': self.parsing_success_rate, 'pattern_matching': 'operational'}}
