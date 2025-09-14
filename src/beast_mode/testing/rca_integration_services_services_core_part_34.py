
def _identify_common_root_causes(self, failures: List[TestFailureData]) -> List[Dict[str, Any]]:
    """Identify potential common root causes across failures"""
    root_causes = []
    failure_types = {}
    for failure in failures:
        if failure.failure_type not in failure_types:
            failure_types[failure.failure_type] = []
        failure_types[failure.failure_type].append(failure)
    for failure_type, type_failures in failure_types.items():
        if len(type_failures) > len(failures) * 0.3:
            root_causes.append({'type': 'failure_type_dominance', 'root_cause': failure_type, 'affected_failures': [f.test_name for f in type_failures], 'confidence': len(type_failures) / len(failures)})
    common_errors = self._find_common_text_patterns([f.error_message for f in failures])
    for error_pattern, count in common_errors.items():
        if count > len(failures) * 0.25:
            root_causes.append({'type': 'common_error_pattern', 'root_cause': error_pattern, 'frequency': count, 'confidence': count / len(failures)})
    return root_causes
