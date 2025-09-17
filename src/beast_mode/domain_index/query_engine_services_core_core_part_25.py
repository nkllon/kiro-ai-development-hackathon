from src.rm_ddd.core.health import ModuleHealth

def _explain_relevance_factors(self, domain: Domain, parsed_query: Dict[str, Any]) -> List[str]:
    """Explain why a domain has high relevance for a query"""
    factors = []
    keywords = parsed_query.get('keywords', [])
    entities = parsed_query.get('entities', {})
    for keyword in keywords:
        if keyword.lower() in domain.name.lower():
            factors.append(f"Domain name contains '{keyword}'")
    for keyword in keywords:
        if keyword.lower() in domain.description.lower():
            factors.append(f"Description mentions '{keyword}'")
    for keyword in keywords:
        matching_patterns = [p for p in domain.patterns if keyword.lower() in p.lower()]
        if matching_patterns:
            factors.append(f"File patterns match '{keyword}': {matching_patterns[0]}")
    for capability in entities.get('capabilities', []):
        if capability in domain.requirements or capability in [domain.tools.linter, domain.tools.formatter]:
            factors.append(f"Domain supports '{capability}' capability")
    return factors

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

