from src.rm_ddd.core.health import ModuleHealth

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

