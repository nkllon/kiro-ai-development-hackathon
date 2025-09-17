from src.rm_ddd.core.health import ModuleHealth

def _find_orphaned_nodes(self, graph: DependencyGraph) -> Set[str]:
    """Find nodes with no dependencies or dependents"""
    orphaned = set()
    for node in graph.nodes:
        has_dependencies = len(graph.get_dependencies(node)) > 0
        has_dependents = len(graph.get_dependents(node)) > 0
        if not has_dependencies and (not has_dependents):
            orphaned.add(node)
    return orphaned

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

