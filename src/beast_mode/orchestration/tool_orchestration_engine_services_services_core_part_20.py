
def _matches_failure_pattern(self, failure_signature: str, pattern: Dict[str, Any]) -> bool:
    """Check if failure signature matches adaptive pattern"""
    pattern_signature = pattern.get('failure_signature', '')
    return any((part in failure_signature for part in pattern_signature.split('|')))
