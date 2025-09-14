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
