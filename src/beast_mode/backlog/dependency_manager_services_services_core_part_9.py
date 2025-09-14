from src.rm_ddd.core.health import ModuleHealth

def get_dependency_graph(self, item_id: str) -> DependencyGraph:
    """
        Get dependency graph for a specific item or the entire graph
        
        Args:
            item_id: Specific item ID or empty string for entire graph
            
        Returns:
            DependencyGraph containing relevant dependencies
        """
    start_time = time.time()
    try:
        full_graph = self._get_cached_graph()
        if not item_id:
            return full_graph
        return self._build_item_subgraph(full_graph, item_id)
    finally:
        self._record_operation_time(time.time() - start_time)

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

