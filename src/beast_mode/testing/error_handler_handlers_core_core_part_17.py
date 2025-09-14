from src.rm_ddd.core.health import ModuleHealth

class AssesserrorseverityClass:
    """Auto-generated class for functions."""

    def _assess_error_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
    """Assess error severity based on type and category"""
    critical_categories = [ErrorCategory.RCA_ENGINE_FAILURE, ErrorCategory.RESOURCE_EXHAUSTION]
    high_categories = [ErrorCategory.TIMEOUT_EXCEEDED, ErrorCategory.CONFIGURATION_ERROR]
    if category in critical_categories:
    return ErrorSeverity.CRITICAL
    elif category in high_categories:
    return ErrorSeverity.HIGH
    elif 'critical' in str(error).lower():
    return ErrorSeverity.CRITICAL
    elif 'error' in str(error).lower():
    return ErrorSeverity.MEDIUM
    else:
    return ErrorSeverity.LOW

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

