from src.rm_ddd.core.health import ModuleHealth

def dfs(node: str):
    if node in rec_stack:
        cycle_start = path.index(node)
        cycle = path[cycle_start:] + [node]
        cycles.append(cycle)
        return
    if node in visited:
        return
    visited.add(node)
    rec_stack.add(node)
    path.append(node)
    for neighbor in graph.edges.get(node, set()):
        dfs(neighbor)
    path.pop()
    rec_stack.remove(node)
