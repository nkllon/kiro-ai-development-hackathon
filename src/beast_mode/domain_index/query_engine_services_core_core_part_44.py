from src.rm_ddd.core.health import ModuleHealth

def _find_similar_domains(self, target_domain: Domain, all_domains: Dict[str, Domain]) -> List[Domain]:
    """Find domains similar to the target domain"""
    similar_domains = []
    target_patterns = set(target_domain.patterns)
    target_indicators = set(target_domain.content_indicators)
    target_requirements = set(target_domain.requirements)
    for domain_name, domain_obj in all_domains.items():
        if domain_name == target_domain.name:
            continue
        pattern_overlap = len(target_patterns.intersection(set(domain_obj.patterns)))
        indicator_overlap = len(target_indicators.intersection(set(domain_obj.content_indicators)))
        requirement_overlap = len(target_requirements.intersection(set(domain_obj.requirements)))
        total_patterns = len(target_patterns.union(set(domain_obj.patterns)))
        total_indicators = len(target_indicators.union(set(domain_obj.content_indicators)))
        total_requirements = len(target_requirements.union(set(domain_obj.requirements)))
        pattern_similarity = pattern_overlap / max(total_patterns, 1)
        indicator_similarity = indicator_overlap / max(total_indicators, 1)
        requirement_similarity = requirement_overlap / max(total_requirements, 1)
        overall_similarity = pattern_similarity * 0.4 + indicator_similarity * 0.3 + requirement_similarity * 0.3
        if overall_similarity > 0.2:
            similar_domains.append(domain_obj)
    similar_domains.sort(key=lambda d: self._calculate_domain_similarity(target_domain, d), reverse=True)
    return similar_domains

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

