
def delete_domain(self, domain_name: str) -> bool:
    """Delete a domain from the registry"""
    with self._time_operation('delete_domain'):
        try:
            if domain_name not in self._domains:
                raise DomainNotFoundError(domain_name)
            del self._domains[domain_name]
            self._index.update_index(Domain(name=domain_name, description='', patterns=[], content_indicators=[], requirements=[], dependencies=[], tools=DomainTools('', '', ''), metadata=DomainMetadata('', '', PackagePotential(0.0, [], [], '', []))))
            self._domain_cache.invalidate_domain(domain_name)
            self.logger.info(f'Deleted domain: {domain_name}')
            return True
        except Exception as e:
            self._handle_error(e, 'delete_domain')
            return False
