from src.rm_ddd.core.health import ModuleHealth

def _analyze_failure(self, failure: InstanceFailure) -> Dict[str, any]:
    """Analyze failure for recovery strategy."""
    return {'severity': 'high' if failure.failure_type in ['crash', 'resource'] else 'medium', 'recoverable': failure.is_recoverable, 'task_impact': len(failure.affected_tasks), 'recovery_complexity': 'simple' if failure.recovery_attempts == 0 else 'complex'}
