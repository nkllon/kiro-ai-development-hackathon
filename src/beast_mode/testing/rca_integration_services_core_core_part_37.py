from src.rm_ddd.core.health import ModuleHealth

class CalculatefailurepriorityscoreClass:
    """Auto-generated class for functions."""

    def _calculate_failure_priority_score(self, failure: TestFailureData) -> float:
    """Calculate priority score for failure (higher = more important)"""
    score = 0.0
    if any((keyword in failure.error_message.lower() for keyword in ['critical', 'fatal', 'system', 'security'])):
    score += 100.0
    if 'ImportError' in failure.error_message:
    score += 50.0
    if any((keyword in failure.error_message.lower() for keyword in ['config', 'setting', 'environment'])):
    score += 30.0
    if any((keyword in failure.test_file.lower() for keyword in ['conftest', 'fixture', 'setup'])):
    score += 40.0
    time_since_failure = (datetime.now() - failure.failure_timestamp).total_seconds()
    if time_since_failure < 300:
    score += 10.0
    return score

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

