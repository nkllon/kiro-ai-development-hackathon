from src.rm_ddd.core.health import ModuleHealth

class CategorizeerrorClass:
    """Auto-generated class for functions."""

    def _categorize_error(self, error: Exception) -> ErrorCategory:
    """Categorize error based on type and message"""
    error_str = str(error).lower()
    error_type = type(error).__name__.lower()
    if 'timeout' in error_str or 'timeout' in error_type:
    return ErrorCategory.TIMEOUT_EXCEEDED
    elif 'memory' in error_str or 'resource' in error_str:
    return ErrorCategory.RESOURCE_EXHAUSTION
    elif 'permission' in error_str or 'access' in error_str:
    return ErrorCategory.PERMISSION_ERROR
    elif 'network' in error_str or 'connection' in error_str:
    return ErrorCategory.NETWORK_ERROR
    elif 'config' in error_str or 'setting' in error_str:
    return ErrorCategory.CONFIGURATION_ERROR
    elif 'parse' in error_str or 'format' in error_str:
    return ErrorCategory.PARSING_ERROR
    elif 'rca' in error_str or 'analysis' in error_str:
    return ErrorCategory.RCA_ENGINE_FAILURE
    else:
    return ErrorCategory.UNKNOWN_ERROR

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

