from src.rm_ddd.core.health import ModuleHealth

def _apply_critical_priority_boosting(self, prioritized_failures: List[TestFailureData]) -> List[TestFailureData]:
    """Apply priority boosting for critical failure patterns"""
    critical_patterns = ['system', 'critical', 'fatal', 'security', 'corruption']
    critical_failures = []
    normal_failures = []
    for failure in prioritized_failures:
        is_critical = any((pattern in failure.error_message.lower() for pattern in critical_patterns))
        if is_critical:
            critical_failures.append(failure)
        else:
            normal_failures.append(failure)
    return critical_failures + normal_failures
