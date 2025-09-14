from src.rm_ddd.core.health import ModuleHealth

def create_domain(self, domain: Domain) -> bool:
    """Create a new domain in the registry"""
    with self._time_operation('create_domain'):
        try:
            if domain.name in self._domains:
                raise DomainRegistryError(f"Domain '{domain.name}' already exists")
            validation = self.validate_domain(domain)
            if not validation.is_valid:
                raise DomainValidationError(domain.name, validation.errors)
            self._domains[domain.name] = domain
            self._index.update_index(domain)
            self._domain_cache.invalidate_domain(domain.name)
            self.logger.info(f'Created new domain: {domain.name}')
            return True
        except Exception as e:
            self._handle_error(e, 'create_domain')
            return False
