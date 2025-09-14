from src.rm_ddd.core.health import ModuleHealth

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
