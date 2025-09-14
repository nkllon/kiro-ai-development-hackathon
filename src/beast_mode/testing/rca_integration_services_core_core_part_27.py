from src.rm_ddd.core.health import ModuleHealth

def _detect_common_failure_patterns(self, failures: List[TestFailureData]) -> List[Dict[str, Any]]:
    """Detect common patterns within a group of failures"""
    patterns = []
    error_messages = [f.error_message for f in failures]
    common_error_patterns = self._find_common_text_patterns(error_messages)
    for pattern in common_error_patterns:
        patterns.append({'type': 'error_message_pattern', 'pattern': pattern, 'frequency': common_error_patterns[pattern]})
    test_files = [f.test_file for f in failures]
    common_file_patterns = self._find_common_text_patterns(test_files)
    for pattern in common_file_patterns:
        patterns.append({'type': 'test_file_pattern', 'pattern': pattern, 'frequency': common_file_patterns[pattern]})
    return patterns
