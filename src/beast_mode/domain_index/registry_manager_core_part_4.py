from src.rm_ddd.core.health import ModuleHealth

def get_domain(self, domain_name: str) -> Optional[Domain]:
    """Retrieve a specific domain by name"""
    cached_domain = self._domain_cache.get_domain(domain_name)
    if cached_domain:
        return cached_domain
    with self._time_operation('get_domain'):
        if not self._registry_loaded:
            self.load_registry()
        domain = self._domains.get(domain_name)
        if not domain:
            raise DomainNotFoundError(domain_name)
        self._domain_cache.cache_domain(domain)
        return domain
