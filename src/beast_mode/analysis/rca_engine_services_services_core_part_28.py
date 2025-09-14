from src.rm_ddd.core.health import ModuleHealth

def _is_make_failure(self, failure: Failure) -> bool:
    """Check if failure is make-related"""
    return 'make' in failure.component.lower() or 'Makefile' in failure.error_message or 'No rule to make target' in failure.error_message or ('missing separator' in failure.error_message)
