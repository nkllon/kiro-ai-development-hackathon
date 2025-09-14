from src.rm_ddd.core.health import ModuleHealth

def validate_dependencies(self, domains: DomainCollection) -> List[HealthIssue]:
    """Validate all domain dependencies"""
    with self._time_operation('validate_dependencies'):
        issues = []
        for domain_name, domain in domains.items():
            for dep in domain.dependencies:
                if dep not in domains:
                    issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.DEPENDENCY, description=f"Domain '{domain_name}' depends on non-existent domain '{dep}'", suggested_fix=f"Either create domain '{dep}' or remove dependency", affected_files=[domain_name]))
        circular_deps = self.detect_circular_dependencies(domains)
        for cycle in circular_deps:
            cycle_str = ' -> '.join(cycle)
            issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.DEPENDENCY, description=f'Circular dependency detected: {cycle_str}', suggested_fix='Refactor to remove circular dependency', affected_files=cycle[:-1]))
        return issues
