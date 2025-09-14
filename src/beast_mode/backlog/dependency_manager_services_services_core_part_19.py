from src.rm_ddd.core.health import ModuleHealth

class CalculatelongestpathClass:
    """Auto-generated class for functions."""

    def _calculate_longest_path(self, graph: DependencyGraph, nodes: Set[str]) -> Tuple[List[str], timedelta]:
    """Calculate longest path through the dependency graph (critical path)"""
    longest_path = []
    max_duration = timedelta(0)
    start_nodes = [node for node in nodes if len(graph.get_dependencies(node)) == 0]
    for start_node in start_nodes:
    path, duration = self._find_longest_path_from_node(graph, start_node, nodes)
    if duration > max_duration:
    longest_path = path
    max_duration = duration
    return (longest_path, max_duration)

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

