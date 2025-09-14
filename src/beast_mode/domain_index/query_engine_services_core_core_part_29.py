
def _combined_search(self, keywords: List[str]) -> List[Domain]:
    """Perform combined search across all indexes"""
    all_results = set()
    for keyword in keywords:
        pattern_results = self.pattern_search(keyword)
        all_results.update((d.name for d in pattern_results))
        content_results = self.content_search(keyword)
        all_results.update((d.name for d in content_results))
        capability_results = self.capability_search(keyword)
        all_results.update((d.name for d in capability_results))
    domains = []
    if self.registry_manager:
        all_domains = self.registry_manager.get_all_domains()
        for domain_name in all_results:
            if domain_name in all_domains:
                domains.append(all_domains[domain_name])
    return domains
