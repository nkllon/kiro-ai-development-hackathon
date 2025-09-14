from src.rm_ddd.core.health import ModuleHealth

def _build_dependency_graph(self) -> DependencyGraph:
    """Build dependency graph from current dependencies"""
    nodes = set()
    edges = defaultdict(set)
    reverse_edges = defaultdict(set)
    for dep_spec in self._dependencies.values():
        if '_depends_on_' in dep_spec.dependency_id:
            source_item = dep_spec.dependency_id.split('_depends_on_')[0]
            target_item = dep_spec.target_item_id
            nodes.add(source_item)
            nodes.add(target_item)
            edges[target_item].add(source_item)
            reverse_edges[source_item].add(target_item)
    return DependencyGraph(nodes=nodes, edges=dict(edges), reverse_edges=dict(reverse_edges), dependency_specs=self._dependencies.copy())

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

