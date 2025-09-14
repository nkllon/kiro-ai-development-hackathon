from src.rm_ddd.core.health import ModuleHealth

def _get_pytest_subcategory(self, failure: Failure) -> str:
    """Get pytest failure subcategory"""
    if 'ImportError' in failure.error_message:
        return 'import_error'
    elif 'AssertionError' in failure.error_message:
        return 'assertion_failure'
    elif 'fixture' in failure.error_message.lower():
        return 'fixture_error'
    elif 'timeout' in failure.error_message.lower():
        return 'timeout'
    else:
        return 'general_pytest_error'
