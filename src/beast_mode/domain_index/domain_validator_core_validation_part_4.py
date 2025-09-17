from src.rm_ddd.core.health import ModuleHealth

def validate_domain_collection(self, domains: DomainCollection) -> Dict[str, ValidationResult]:
    """Validate all domains in a collection"""
    with self._time_operation('validate_domain_collection'):
        results = {}
        for domain_name, domain in domains.items():
            context = {'all_domains': domains}
            results[domain_name] = self.validate_domain(domain, context)
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

