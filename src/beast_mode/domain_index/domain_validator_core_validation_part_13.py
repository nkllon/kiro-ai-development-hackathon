from src.rm_ddd.core.health import ModuleHealth

def validate_required_fields(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    for field in self.required_fields:
        if not hasattr(domain, field) or not getattr(domain, field):
            issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' missing required field: {field}", suggested_fix=f'Add {field} to domain definition'))
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

