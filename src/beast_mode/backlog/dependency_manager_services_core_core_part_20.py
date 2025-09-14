from src.rm_ddd.core.health import ModuleHealth

def _find_longest_path_from_node(self, graph: DependencyGraph, start_node: str, valid_nodes: Set[str]) -> Tuple[List[str], timedelta]:
    """Find longest path from a specific starting node"""
    visited = set()
    path = [start_node]
    duration = timedelta(0)
