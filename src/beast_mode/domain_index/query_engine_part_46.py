
def _detect_circular_dependencies(self, domain_name: str, all_domains: Dict[str, Domain]) -> List[List[str]]:
    """Detect circular dependency chains involving the given domain"""
    circular_chains = []
