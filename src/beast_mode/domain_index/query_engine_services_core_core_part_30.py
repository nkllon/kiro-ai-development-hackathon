from src.rm_ddd.core.health import ModuleHealth

def _calculate_relevance_scores(self, domains: List[Domain], keywords: List[str]) -> Dict[str, float]:
    """Calculate enhanced relevance scores for search results"""
    scores = {}
    for domain in domains:
        score = 0.0
        for keyword in keywords:
            if keyword.lower() == domain.name.lower():
                score += 5.0
            elif keyword.lower() in domain.name.lower():
                score += 3.0
        for keyword in keywords:
            if keyword.lower() in domain.description.lower():
                if f' {keyword.lower()} ' in f' {domain.description.lower()} ':
                    score += 2.5
                else:
                    score += 2.0
        for keyword in keywords:
            for pattern in domain.patterns:
                if keyword.lower() in pattern.lower():
                    score += 1.0
        for keyword in keywords:
            for indicator in domain.content_indicators:
                if keyword.lower() == indicator.lower():
                    score += 2.0
                elif keyword.lower() in indicator.lower():
                    score += 1.5
        for keyword in keywords:
            for requirement in domain.requirements:
                if keyword.lower() in requirement.lower():
                    score += 1.2
        tool_names = [domain.tools.linter, domain.tools.formatter, domain.tools.validator]
        tool_names.extend(domain.tools.custom_tools.values())
        for keyword in keywords:
            for tool in tool_names:
                if tool and keyword.lower() in tool.lower():
                    score += 1.0
        for keyword in keywords:
            if keyword.lower() in domain.metadata.demo_role.lower():
                score += 1.5
            for tag in domain.metadata.tags:
                if keyword.lower() in tag.lower():
                    score += 1.0
        if domain.health_status:
            if domain.health_status.status.value == 'healthy':
                score *= 1.1
            elif domain.health_status.status.value == 'degraded':
                score *= 0.9
            elif domain.health_status.status.value == 'failed':
                score *= 0.7
        if domain.metadata.extraction_candidate == 'high':
            score *= 1.05
        scores[domain.name] = score
    return scores

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

