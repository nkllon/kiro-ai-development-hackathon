from src.rm_ddd.core.health import ModuleHealth

class CalculatefailureimpactscoreClass:
    """Auto-generated class for functions."""

    def _calculate_failure_impact_score(self, failure: TestFailureData) -> float:
    """Calculate impact score based on failure characteristics"""
    impact_score = 0.0
    if any((keyword in failure.test_file.lower() for keyword in ['conftest', 'fixture', 'setup', '__init__'])):
    impact_score += 50.0
    if failure.failure_type == 'import':
    impact_score += 40.0
    if any((keyword in failure.error_message.lower() for keyword in ['config', 'environment', 'setting'])):
    impact_score += 30.0
    if any((keyword in failure.error_message.lower() for keyword in ['security', 'permission', 'access', 'auth'])):
    impact_score += 35.0
    return impact_score

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

