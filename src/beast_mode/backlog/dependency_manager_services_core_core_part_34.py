from src.rm_ddd.core.health import ModuleHealth

def collect_reachable(node: str, visited: Set[str]):
    if node in visited:
        return
    visited.add(node)
    reachable_nodes.add(node)
    for dep in full_graph.get_dependencies(node):
        collect_reachable(dep, visited)
    for dep in full_graph.get_dependents(node):
        collect_reachable(dep, visited)
