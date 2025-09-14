from src.rm_ddd.core.health import ModuleHealth

def _analyze_temporal_correlations(self, failures: List[TestFailureData]) -> List[Dict[str, Any]]:
    """Analyze temporal correlations between failures"""
    correlations = []
    sorted_failures = sorted(failures, key=lambda f: f.failure_timestamp)
    for i in range(len(sorted_failures) - 1):
        current = sorted_failures[i]
        next_failure = sorted_failures[i + 1]
        time_diff = (next_failure.failure_timestamp - current.failure_timestamp).total_seconds()
        if time_diff < 60:
            correlations.append({'type': 'temporal', 'failures': [current.test_name, next_failure.test_name], 'time_difference_seconds': time_diff, 'correlation_strength': max(0.0, 1.0 - time_diff / 60.0)})
    return correlations
