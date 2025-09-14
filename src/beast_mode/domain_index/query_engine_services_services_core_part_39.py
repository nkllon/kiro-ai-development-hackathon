
def _calculate_enhanced_relevance_scores(self, domains: List[Domain], parsed_query: Dict[str, Any]) -> Dict[str, float]:
    """Calculate relevance scores using parsed query information"""
    scores = {}
    keywords = parsed_query.get('keywords', [])
    entities = parsed_query.get('entities', {})
    intent = parsed_query.get('intent', 'general_search')
    for domain in domains:
        score = 0.0
        base_scores = self._calculate_relevance_scores([domain], keywords)
        score += base_scores.get(domain.name, 0.0)
        for domain_name in entities.get('domain_names', []):
            if domain_name.lower() in domain.name.lower():
                score += 5.0
        for pattern in entities.get('patterns', []):
            if any((pattern.lower() in p.lower() for p in domain.patterns)):
                score += 3.0
        for capability in entities.get('capabilities', []):
            if self._calculate_capability_relevance(domain, capability) > 0:
                score += 2.0
        if intent == 'capability_search':
            score += self._calculate_capability_relevance(domain, ' '.join(keywords))
        elif intent == 'pattern_search':
            pattern_matches = sum((1 for keyword in keywords for pattern in domain.patterns if keyword.lower() in pattern.lower()))
            score += pattern_matches * 1.5
        scores[domain.name] = score
    return scores
