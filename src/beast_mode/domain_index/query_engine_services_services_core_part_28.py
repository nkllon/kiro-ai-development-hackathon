from src.rm_ddd.core.health import ModuleHealth

def _search_by_capabilities(self, keywords: List[str]) -> List[Domain]:
    """Search domains by capability keywords"""
    results = []
    seen_names = set()
    for keyword in keywords:
        for domain in self.capability_search(keyword):
            if domain.name not in seen_names:
                results.append(domain)
                seen_names.add(domain.name)
    return results
