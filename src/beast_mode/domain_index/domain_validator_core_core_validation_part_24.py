
def check_orphaned_dependencies(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    all_dependencies = set()
    domain_names = set(domains.keys())
    for domain in domains.values():
        all_dependencies.update(domain.dependencies)
    orphaned = all_dependencies - domain_names
    for orphan in orphaned:
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.DEPENDENCY, description=f"Dependency '{orphan}' is referenced but no domain exists", suggested_fix=f"Create domain '{orphan}' or remove references to it"))
    return issues
