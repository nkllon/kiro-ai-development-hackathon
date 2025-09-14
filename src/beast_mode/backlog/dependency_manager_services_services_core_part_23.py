from src.rm_ddd.core.health import ModuleHealth

def _identify_bottlenecks(self, graph: DependencyGraph, critical_path: List[str]) -> List[str]:
    """Identify bottleneck nodes in the critical path"""
    bottlenecks = []
    for node in critical_path:
        dependent_count = len(graph.get_dependents(node))
        if dependent_count > 2:
            bottlenecks.append(node)
    return bottlenecks
