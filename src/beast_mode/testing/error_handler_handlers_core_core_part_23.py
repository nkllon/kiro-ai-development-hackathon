from src.rm_ddd.core.health import ModuleHealth

def _perform_basic_failure_analysis(self, test_failures: List[Any]) -> Dict[str, Any]:
    """Perform basic analysis when RCA engine is unavailable"""
    failure_types = {}
    error_patterns = {}
    for failure in test_failures:
        failure_types[failure.failure_type] = failure_types.get(failure.failure_type, 0) + 1
        error_words = failure.error_message.lower().split()[:5]
        pattern = ' '.join(error_words)
        error_patterns[pattern] = error_patterns.get(pattern, 0) + 1
    return {'failure_types': failure_types, 'error_patterns': error_patterns, 'total_failures': len(test_failures)}
