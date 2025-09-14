from src.rm_ddd.core.health import ModuleHealth

def _calculate_coupling_score(self, domain1: Domain, domain2: Domain) -> float:
    """Calculate coupling score between two domains"""
    score = 0.0
    if domain2.name in domain1.dependencies:
        score += 0.4
    if domain1.name in domain2.dependencies:
        score += 0.4
    pattern_overlap = len(set(domain1.patterns).intersection(set(domain2.patterns)))
    if pattern_overlap > 0:
        score += 0.2 * min(pattern_overlap / len(domain1.patterns), 1.0)
    if domain1.tools.linter == domain2.tools.linter:
        score += 0.1
    if domain1.tools.formatter == domain2.tools.formatter:
        score += 0.1
    return min(score, 1.0)
