from src.rm_ddd.core.health import ModuleHealth

class DeterminefailuretypeClass:
    """Auto-generated class for functions."""

    def _determine_failure_type(self, error_message: str) -> str:
    """Determine failure type from error message"""
    error_lower = error_message.lower()
    if 'assertionerror' in error_lower or 'assert' in error_lower:
    return 'assertion'
    elif 'importerror' in error_lower or 'modulenotfounderror' in error_lower:
    return 'import'
    elif 'filenotfounderror' in error_lower:
    return 'file_not_found'
    elif 'permissionerror' in error_lower:
    return 'permission'
    elif 'timeout' in error_lower:
    return 'timeout'
    elif 'connectionerror' in error_lower or 'network' in error_lower:
    return 'network'
    elif 'memoryerror' in error_lower:
    return 'memory'
    else:
    return 'error'

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

