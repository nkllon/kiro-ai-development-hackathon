from src.rm_ddd.core.health import ModuleHealth

def _build_dependency_graph(self, tasks: List[Task]) -> Dict[str, List[str]]:
    """Build task dependency graph for analysis."""
    graph = {}
    for task in tasks:
        graph[task.id] = task.dependencies.copy()
    return graph
