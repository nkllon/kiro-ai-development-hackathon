
def _calculate_capability_relevance(self, domain: Domain, capability: str) -> float:
    """Calculate how relevant a domain is for a given capability"""
    relevance_score = 0.0
    if capability in domain.name.lower():
        relevance_score += 3.0
    for requirement in domain.requirements:
        if self._capability_matches(capability, requirement.lower()):
            relevance_score += 2.0
    tool_capabilities = [domain.tools.linter, domain.tools.formatter, domain.tools.validator]
    tool_capabilities.extend(domain.tools.custom_tools.values())
    for tool in tool_capabilities:
        if tool and self._capability_matches(capability, tool.lower()):
            relevance_score += 1.5
    for indicator in domain.content_indicators:
        if self._capability_matches(capability, indicator.lower()):
            relevance_score += 1.0
    for pattern in domain.patterns:
        if self._pattern_suggests_capability(pattern, capability):
            relevance_score += 0.5
    return relevance_score
