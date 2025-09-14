from src.rm_ddd.core.health import ModuleHealth

class CalculatefailuresimilarityClass:
    """Auto-generated class for functions."""

    def _calculate_failure_similarity(self, failure_a: TestFailureData, failure_b: TestFailureData) -> float:
    """Calculate similarity score between two failures"""
    similarity = 0.0
    if failure_a.test_file == failure_b.test_file:
    similarity += 0.3
    if failure_a.failure_type == failure_b.failure_type:
    similarity += 0.2
    error_similarity = self._calculate_text_similarity(failure_a.error_message, failure_b.error_message)
    similarity += error_similarity * 0.3
    if failure_a.stack_trace and failure_b.stack_trace:
    trace_similarity = self._calculate_text_similarity(failure_a.stack_trace, failure_b.stack_trace)
    similarity += trace_similarity * 0.2
    return min(similarity, 1.0)

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

