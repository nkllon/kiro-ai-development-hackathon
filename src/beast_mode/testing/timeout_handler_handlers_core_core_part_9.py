from src.rm_ddd.core.health import ModuleHealth

def optimize_timeout_configuration(self) -> Dict[str, Any]:
    """
        Optimize timeout configuration based on historical performance
        Requirements: 4.2 - Performance optimization
        """
    try:
        optimization_result = {'optimization_applied': False, 'previous_config': {'primary_timeout': self.timeout_config.primary_timeout_seconds, 'warning_timeout': self.timeout_config.warning_timeout_seconds, 'graceful_timeout': self.timeout_config.graceful_timeout_seconds}, 'new_config': {}, 'optimization_reason': '', 'performance_improvement_expected': 0.0}
        if len(self.timeout_events) < 10:
            optimization_result['optimization_reason'] = 'insufficient_data'
            return optimization_result
        recent_events = self.timeout_events[-50:]
        completed_operations = [e for e in recent_events if e.operation_completed]
        if completed_operations:
            avg_completion_time = sum((e.elapsed_seconds for e in completed_operations)) / len(completed_operations)
            if avg_completion_time < self.timeout_config.primary_timeout_seconds * 0.6:
                new_primary = max(15, int(avg_completion_time * 1.5))
                new_warning = max(10, int(new_primary * 0.8))
                new_graceful = max(8, int(new_primary * 0.7))
                self.timeout_config.primary_timeout_seconds = new_primary
                self.timeout_config.warning_timeout_seconds = new_warning
                self.timeout_config.graceful_timeout_seconds = new_graceful
                optimization_result.update({'optimization_applied': True, 'new_config': {'primary_timeout': new_primary, 'warning_timeout': new_warning, 'graceful_timeout': new_graceful}, 'optimization_reason': 'operations_completing_faster_than_expected', 'performance_improvement_expected': 0.2})
            elif avg_completion_time > self.timeout_config.primary_timeout_seconds * 0.9:
                new_primary = min(45, int(avg_completion_time * 1.2))
                new_warning = int(new_primary * 0.8)
                new_graceful = int(new_primary * 0.7)
                self.timeout_config.primary_timeout_seconds = new_primary
                self.timeout_config.warning_timeout_seconds = new_warning
                self.timeout_config.graceful_timeout_seconds = new_graceful
                optimization_result.update({'optimization_applied': True, 'new_config': {'primary_timeout': new_primary, 'warning_timeout': new_warning, 'graceful_timeout': new_graceful}, 'optimization_reason': 'operations_approaching_timeout_limits', 'performance_improvement_expected': 0.1})
        self.logger.info(f'Timeout configuration optimization: {optimization_result}')
        return optimization_result
    except Exception as e:
        self.logger.error(f'Timeout configuration optimization failed: {e}')
        return {'optimization_applied': False, 'error': str(e)}
