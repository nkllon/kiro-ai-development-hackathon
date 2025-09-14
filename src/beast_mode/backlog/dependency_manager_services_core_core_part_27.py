from src.rm_ddd.core.health import ModuleHealth

class CollectreachableClass:
    """Auto-generated class for functions."""

    def collect_reachable(node: str, visited: Set[str]):
    if node in visited:
    return
    visited.add(node)
    reachable_nodes.add(node)
    for dep in full_graph.get_dependencies(node):
    collect_reachable(dep, visited)
    for dep in full_graph.get_dependents(node):
    collect_reachable(dep, visited)
    collect_reachable(item_id, set())
    sub_edges = {}
    sub_reverse_edges = {}
    for node in reachable_nodes:
    sub_edges[node] = full_graph.edges.get(node, set()) & reachable_nodes
    sub_reverse_edges[node] = full_graph.reverse_edges.get(node, set()) & reachable_nodes
    return DependencyGraph(nodes=reachable_nodes, edges=sub_edges, reverse_edges=sub_reverse_edges, dependency_specs=full_graph.dependency_specs)

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

