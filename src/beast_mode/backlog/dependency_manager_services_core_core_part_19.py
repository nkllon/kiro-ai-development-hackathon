
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
