from src.rm_ddd.core.health import ModuleHealth

class CalculatecorrelationpriorityscoreClass:
    """Auto-generated class for functions."""

    def _calculate_correlation_priority_score(self, failure: TestFailureData, all_failures: List[TestFailureData]) -> float:
    """Calculate priority score based on correlation with other failures"""
    correlation_score = 0.0
    similar_failures = 0
    for other_failure in all_failures:
    if other_failure != failure:
    similarity = self._calculate_failure_similarity(failure, other_failure)
    if similarity > 0.5:
    similar_failures += 1
    correlation_score = min(similar_failures * 10.0, 50.0)
    return correlation_score

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

