
def search_by_category(self, category: str) -> List[Domain]:
    """Search domains by category"""
    domain_names = self._index.search_by_category(category)
    return [self.get_domain(name) for name in domain_names if name in self._domains]
