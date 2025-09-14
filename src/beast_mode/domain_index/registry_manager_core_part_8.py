
def get_dependencies(self, domain_name: str) -> DependencyGraph:
    """Get dependency graph for a domain"""
    with self._time_operation('get_dependencies'):
        domain = self.get_domain(domain_name)
        return DependencyGraph(domain=domain_name, direct_dependencies=domain.dependencies, transitive_dependencies=[], dependents=[], circular_dependencies=[], dependency_depth=len(domain.dependencies), coupling_score=0.5)
