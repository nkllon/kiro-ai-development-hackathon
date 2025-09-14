from src.rm_ddd.core.health import ModuleHealth

def _find_extraction_related_domains(self, target_domain: Domain, all_domains: Dict[str, Domain]) -> List[Domain]:
    """Find domains that would be affected by extracting the target domain"""
    related_domains = []
    for domain_name, domain_obj in all_domains.items():
        if target_domain.name in domain_obj.dependencies:
            related_domains.append(domain_obj)
    target_patterns = set(target_domain.patterns)
    for domain_name, domain_obj in all_domains.items():
        if domain_name == target_domain.name:
            continue
        pattern_overlap = len(target_patterns.intersection(set(domain_obj.patterns)))
        if pattern_overlap > 0:
            related_domains.append(domain_obj)
    seen = set()
    unique_related = []
    for domain in related_domains:
        if domain.name not in seen:
            seen.add(domain.name)
            unique_related.append(domain)
    return unique_related
