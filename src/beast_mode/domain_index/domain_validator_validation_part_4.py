from src.rm_ddd.core.health import ModuleHealth

def validate_domain_collection(self, domains: DomainCollection) -> Dict[str, ValidationResult]:
    """Validate all domains in a collection"""
    with self._time_operation('validate_domain_collection'):
        results = {}
        for domain_name, domain in domains.items():
            context = {'all_domains': domains}
            results[domain_name] = self.validate_domain(domain, context)
        return results
