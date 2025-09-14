from src.rm_ddd.core.health import ModuleHealth

def _generate_failure_group_key(self, failure: TestFailureData) -> str:
    """Generate grouping key for related failures"""
    error_type = failure.failure_type
    test_module = failure.test_file.split('/')[-1].replace('.py', '')
    error_signature = ''
    if 'ImportError' in failure.error_message:
        error_signature = 'import_error'
    elif 'AssertionError' in failure.error_message:
        error_signature = 'assertion_error'
    elif 'FileNotFoundError' in failure.error_message:
        error_signature = 'file_not_found'
    elif 'PermissionError' in failure.error_message:
        error_signature = 'permission_error'
    else:
        error_signature = 'other_error'
    return f'{test_module}_{error_type}_{error_signature}'
