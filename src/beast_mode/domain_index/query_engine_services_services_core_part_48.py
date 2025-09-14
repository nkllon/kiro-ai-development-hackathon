
def _find_high_coupling_domains(self, target_domain: Domain, all_domains: Dict[str, Domain]) -> List[Domain]:
    """Find domains with high coupling to the target domain"""
    high_coupling_domains = []
    for domain_name, domain_obj in all_domains.items():
        if domain_name == target_domain.name:
            continue
        coupling_score = self._calculate_coupling_score(target_domain, domain_obj)
        if coupling_score > 0.5:
            high_coupling_domains.append(domain_obj)
    high_coupling_domains.sort(key=lambda d: self._calculate_coupling_score(target_domain, d), reverse=True)
    return high_coupling_domains
