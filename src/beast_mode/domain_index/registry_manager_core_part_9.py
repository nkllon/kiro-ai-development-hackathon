
def update_domain(self, domain: Domain) -> bool:
    """Update a domain in the registry"""
    with self._time_operation('update_domain'):
        try:
            validation = self.validate_domain(domain)
            if not validation.is_valid:
                raise DomainValidationError(domain.name, validation.errors)
            self._domains[domain.name] = domain
            self._index.update_index(domain)
            self._domain_cache.invalidate_domain(domain.name)
            self.logger.info(f'Updated domain: {domain.name}')
            return True
        except Exception as e:
            self._handle_error(e, 'update_domain')
            return False
