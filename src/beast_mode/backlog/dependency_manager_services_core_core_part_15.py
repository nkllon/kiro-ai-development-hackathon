from src.rm_ddd.core.health import ModuleHealth

def _find_cycles_dfs(self, graph: DependencyGraph) -> List[List[str]]:
    """Find all cycles in the dependency graph using DFS"""
    cycles = []
    visited = set()
    rec_stack = set()
    path = []
