from src.rm_ddd.core.health import ModuleHealth

def search_domains(self, query: str, filters: Optional[Dict[str, Any]]=None) -> List[Domain]:
    """Search domains with optional filters using the index"""
    with self._time_operation('search_domains'):
        domain_names = self._index.search_index(query, filters)
        results = []
        for domain_name in domain_names:
            try:
                domain = self.get_domain(domain_name)
                if domain:
                    results.append(domain)
            except DomainNotFoundError:
                continue
        return results
