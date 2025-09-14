from src.rm_ddd.core.health import ModuleHealth

def _verify_pattern_match(self, failure: Failure, pattern: PreventionPattern) -> bool:
    """Verify if failure matches existing pattern"""
    failure_signature = self._generate_failure_signature(failure)
    return failure.component in pattern.failure_signature and failure.category.value in pattern.failure_signature
