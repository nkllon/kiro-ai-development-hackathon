from src.rm_ddd.core.health import ModuleHealth

class SearchbycontentClass:
    """Auto-generated class for functions."""

    def _search_by_content(self, keywords: List[str]) -> List[Domain]:
    """Search domains by content keywords"""
    results = []
    seen_names = set()
    for keyword in keywords:
    for domain in self.content_search(keyword):
    if domain.name not in seen_names:
    results.append(domain)
    seen_names.add(domain.name)
    return results

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

