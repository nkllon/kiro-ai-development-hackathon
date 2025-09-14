from src.rm_ddd.core.health import ModuleHealth

class ApplycriticalpriorityboostingClass:
    """Auto-generated class for functions."""

    def _apply_critical_priority_boosting(self, prioritized_failures: List[TestFailureData]) -> List[TestFailureData]:
    """Apply priority boosting for critical failure patterns"""
    critical_patterns = ['system', 'critical', 'fatal', 'security', 'corruption']
    critical_failures = []
    normal_failures = []
    for failure in prioritized_failures:
    is_critical = any((pattern in failure.error_message.lower() for pattern in critical_patterns))
    if is_critical:
    critical_failures.append(failure)
    else:
    normal_failures.append(failure)
    return critical_failures + normal_failures

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

