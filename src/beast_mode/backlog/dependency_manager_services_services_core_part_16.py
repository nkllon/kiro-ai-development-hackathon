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
    for node in graph.nodes:
        if node not in visited:
            dfs(node)
    return cycles

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

