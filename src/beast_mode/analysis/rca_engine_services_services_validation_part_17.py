from src.rm_ddd.core.health import ModuleHealth

def _generate_test_failure_signature(self, failure: Failure) -> str:
    """Generate test-specific failure signature for pattern matching"""
    signature_parts = [failure.component, failure.category.value, failure.error_message[:100] if failure.error_message else '', failure.context.get('test_file', '') if failure.context else '', failure.context.get('failure_type', '') if failure.context else '', str(sorted(failure.context.keys())) if failure.context else '']
    return '|'.join(signature_parts)
