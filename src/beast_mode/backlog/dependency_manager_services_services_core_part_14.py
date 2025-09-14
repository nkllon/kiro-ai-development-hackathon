from src.rm_ddd.core.health import ModuleHealth

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

