from src.rm_ddd.core.health import ModuleHealth

class IdentifybottlenecksClass:
    """Auto-generated class for functions."""

    def _identify_bottlenecks(self, graph: DependencyGraph, critical_path: List[str]) -> List[str]:
    """Identify bottleneck nodes in the critical path"""
    bottlenecks = []
    for node in critical_path:
    dependent_count = len(graph.get_dependents(node))
    if dependent_count > 2:
    bottlenecks.append(node)
    return bottlenecks

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

