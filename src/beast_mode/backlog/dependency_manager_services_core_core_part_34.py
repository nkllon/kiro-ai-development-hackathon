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

