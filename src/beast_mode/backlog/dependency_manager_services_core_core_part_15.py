from src.rm_ddd.core.health import ModuleHealth

def _find_cycles_dfs(self, graph: DependencyGraph) -> List[List[str]]:
    """Find all cycles in the dependency graph using DFS"""
    cycles = []
    visited = set()
    rec_stack = set()
    path = []

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

