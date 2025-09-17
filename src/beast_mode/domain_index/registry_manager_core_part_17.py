from src.rm_ddd.core.health import ModuleHealth

def search_by_pattern(self, pattern: str) -> List[Domain]:
    """Search domains by file pattern"""
    domain_names = self._index.search_by_pattern(pattern)
    return [self.get_domain(name) for name in domain_names if name in self._domains]

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

