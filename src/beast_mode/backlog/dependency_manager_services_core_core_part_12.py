from src.rm_ddd.core.health import ModuleHealth

def _would_create_cycle(self, source_item: str, target_item: str, temp_deps: Dict[str, DependencySpec]) -> bool:
    """Check if adding a dependency would create a cycle"""
    if source_item == target_item:
        return False
    temp_graph = self._build_temp_graph(temp_deps)
    if target_item not in temp_graph:
        temp_graph[target_item] = set()
    temp_graph[target_item].add(source_item)
    return self._has_path(temp_graph, source_item, target_item)

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

