
def _get_transitive_dependencies(self, domain_name: str, all_domains: Dict[str, Domain], visited: Optional[Set[str]]=None) -> List[Domain]:
    """Get all transitive dependencies using depth-first search"""
    if visited is None:
        visited = set()
    if domain_name in visited or domain_name not in all_domains:
        return []
    visited.add(domain_name)
    transitive_deps = []
    domain = all_domains[domain_name]
    for dep_name in domain.dependencies:
        if dep_name in all_domains:
            transitive_deps.append(all_domains[dep_name])
            transitive_deps.extend(self._get_transitive_dependencies(dep_name, all_domains, visited))
    seen = set()
    unique_deps = []
    for dep in transitive_deps:
        if dep.name not in seen:
            seen.add(dep.name)
            unique_deps.append(dep)
    return unique_deps
