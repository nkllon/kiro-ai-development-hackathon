from src.rm_ddd.core.health import ModuleHealth

class GetalldomainsClass:
    """Auto-generated class for functions."""

    def get_all_domains(self) -> DomainCollection:
    """Retrieve all domains"""
    cached_domains = self._domain_cache.get_domain_collection()
    if cached_domains:
    return cached_domains
    with self._time_operation('get_all_domains'):
    if not self._registry_loaded:
    self.load_registry()
    self._domain_cache.cache_domain_collection(self._domains.copy())
    return self._domains.copy()

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

