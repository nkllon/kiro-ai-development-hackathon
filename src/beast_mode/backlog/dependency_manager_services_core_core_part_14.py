
def _has_path(self, graph: Dict[str, Set[str]], start: str, end: str) -> bool:
    """Check if there's a path from start to end in the graph using BFS"""
    if start == end:
        return True
    visited = set()
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        for neighbor in graph.get(current, set()):
            if neighbor == end:
                return True
            if neighbor not in visited:
                queue.append(neighbor)
    return False
