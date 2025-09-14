from src.rm_ddd.core.health import ModuleHealth

def _generate_failure_signature(self, failure: Failure) -> str:
    """Generate unique signature for failure pattern matching"""
    signature_parts = [failure.component, failure.category.value, failure.error_message[:100] if failure.error_message else '', str(sorted(failure.context.keys())) if failure.context else '']
    return '|'.join(signature_parts)
