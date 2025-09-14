from src.rm_ddd.core.health import ModuleHealth

def search_by_pattern(self, pattern: str) -> List[Domain]:
    """Search domains by file pattern"""
    domain_names = self._index.search_by_pattern(pattern)
    return [self.get_domain(name) for name in domain_names if name in self._domains]
