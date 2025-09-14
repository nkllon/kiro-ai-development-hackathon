
def get_module_status(self) -> Dict[str, Any]:
    """Operational visibility for external systems"""
    return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'test_runs_monitored': self.total_test_runs_monitored, 'failures_detected': self.total_failures_detected, 'parsing_success_rate': self.parsing_success_rate, 'degradation_active': self._degradation_active}
