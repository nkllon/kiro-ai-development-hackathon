from src.rm_ddd.core.health import ModuleHealth

class AnalyzefailureClass:
    """Auto-generated class for functions."""

    def _analyze_failure(self, failure: InstanceFailure) -> Dict[str, any]:
    """Analyze failure for recovery strategy."""
    return {'severity': 'high' if failure.failure_type in ['crash', 'resource'] else 'medium', 'recoverable': failure.is_recoverable, 'task_impact': len(failure.affected_tasks), 'recovery_complexity': 'simple' if failure.recovery_attempts == 0 else 'complex'}

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

