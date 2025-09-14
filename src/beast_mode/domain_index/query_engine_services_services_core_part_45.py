from src.rm_ddd.core.health import ModuleHealth

def _calculate_domain_similarity(self, domain1: Domain, domain2: Domain) -> float:
    """Calculate similarity score between two domains"""
    patterns1 = set(domain1.patterns)
    patterns2 = set(domain2.patterns)
    indicators1 = set(domain1.content_indicators)
    indicators2 = set(domain2.content_indicators)
    requirements1 = set(domain1.requirements)
    requirements2 = set(domain2.requirements)
    pattern_jaccard = len(patterns1.intersection(patterns2)) / len(patterns1.union(patterns2)) if patterns1.union(patterns2) else 0
    indicator_jaccard = len(indicators1.intersection(indicators2)) / len(indicators1.union(indicators2)) if indicators1.union(indicators2) else 0
    requirement_jaccard = len(requirements1.intersection(requirements2)) / len(requirements1.union(requirements2)) if requirements1.union(requirements2) else 0
    return pattern_jaccard * 0.4 + indicator_jaccard * 0.3 + requirement_jaccard * 0.3
