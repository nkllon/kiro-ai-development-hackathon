from src.rm_ddd.core.health import ModuleHealth

class CheckdependenciesClass:
    """Auto-generated class for functions."""

    def _check_dependencies(self, domain: Domain) -> List[HealthIssue]:
    """Check if domain dependencies exist and are accessible"""
    issues = []
    if not self.registry_manager:
    return issues
    try:
    all_domains = self.registry_manager.get_all_domains()
    for dependency in domain.dependencies:
    if dependency not in all_domains:
    issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.DEPENDENCY, description=f"Dependency '{dependency}' not found in registry", suggested_fix=f"Add '{dependency}' to registry or remove from dependencies"))
    else:
    dep_domain = all_domains[dependency]
    if hasattr(dep_domain, 'health_status') and dep_domain.health_status:
    if dep_domain.health_status.status == HealthStatusType.FAILED:
    issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.DEPENDENCY, description=f"Dependency '{dependency}' has failed health status", suggested_fix=f"Resolve health issues in '{dependency}' domain"))
    except Exception as e:
    issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.DEPENDENCY, description=f'Failed to validate dependencies: {str(e)}', suggested_fix='Check registry accessibility and dependency configuration'))
    return issues

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

