
def _generate_failure_signature(self, failure_context: Dict[str, Any]) -> str:
    """Generate signature for failure pattern matching"""
    signature_parts = [failure_context.get('tool_name', 'unknown'), failure_context.get('error_type', 'unknown'), failure_context.get('failure_category', 'unknown'), str(failure_context.get('exit_code', 'unknown'))]
    return '|'.join(signature_parts)
