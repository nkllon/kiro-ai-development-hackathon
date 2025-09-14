from src.rm_ddd.core.health import ModuleHealth

class BuildtempgraphClass:
    """Auto-generated class for functions."""

    def _build_temp_graph(self, temp_deps: Dict[str, DependencySpec]) -> Dict[str, Set[str]]:
    """Build temporary graph for cycle detection"""
    graph = defaultdict(set)
    for dep_spec in temp_deps.values():
    if '_depends_on_' in dep_spec.dependency_id:
    source_item = dep_spec.dependency_id.split('_depends_on_')[0]
    target_item = dep_spec.target_item_id
    graph[target_item].add(source_item)
    return dict(graph)

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

