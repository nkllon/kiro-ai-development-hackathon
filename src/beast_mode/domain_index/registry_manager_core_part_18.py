from src.rm_ddd.core.health import ModuleHealth

class SearchbycategoryClass:
    """Auto-generated class for functions."""

    def search_by_category(self, category: str) -> List[Domain]:
    """Search domains by category"""
    domain_names = self._index.search_by_category(category)
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

