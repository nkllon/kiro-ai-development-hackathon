from src.rm_ddd.core.health import ModuleHealth

def get_domain_relationships(self, domain_name: str) -> Dict[str, List[str]]:
    """Get domain relationships from index"""
    return self._index.get_domain_relationships(domain_name)
