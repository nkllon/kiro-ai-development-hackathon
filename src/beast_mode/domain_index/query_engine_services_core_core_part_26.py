
def _search_by_patterns(self, keywords: List[str]) -> List[Domain]:
    """Search domains by pattern keywords"""
    results = []
    seen_names = set()
    for keyword in keywords:
        for domain in self.pattern_search(keyword):
            if domain.name not in seen_names:
                results.append(domain)
                seen_names.add(domain.name)
    return results
