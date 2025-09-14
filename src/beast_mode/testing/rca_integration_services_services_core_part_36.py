from src.rm_ddd.core.health import ModuleHealth

class GeneratefailuregroupkeyClass:
    """Auto-generated class for functions."""

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

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

