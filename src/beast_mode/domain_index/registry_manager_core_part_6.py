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

