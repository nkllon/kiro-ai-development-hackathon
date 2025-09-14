from src.rm_ddd.core.health import ModuleHealth

def _get_transitive_dependents(self, domain_name: str, all_domains: Dict[str, Domain]) -> List[Domain]:
    """Get all domains that transitively depend on this domain"""
    transitive_dependents = []
    reverse_deps = {}
    for name, domain in all_domains.items():
        for dep in domain.dependencies:
            if dep not in reverse_deps:
                reverse_deps[dep] = []
            reverse_deps[dep].append(name)
    visited = set()
    queue = [domain_name]
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        if current in reverse_deps:
            for dependent in reverse_deps[current]:
                if dependent not in visited and dependent in all_domains:
                    transitive_dependents.append(all_domains[dependent])
                    queue.append(dependent)
    return transitive_dependents
