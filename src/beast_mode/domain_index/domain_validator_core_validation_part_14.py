from src.rm_ddd.core.health import ModuleHealth

def validate_domain_name(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    if not domain.name:
        issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description='Domain name is empty', suggested_fix='Provide a valid domain name'))
        return issues
    if not re.match('^[a-z][a-z0-9_]*$', domain.name):
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f"Domain name '{domain.name}' doesn't follow naming convention", suggested_fix='Use lowercase letters, numbers, and underscores only'))
    reserved_names = {'test', 'temp', 'tmp', 'debug', 'admin'}
    if domain.name.lower() in reserved_names:
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f"Domain name '{domain.name}' is reserved", suggested_fix='Choose a more descriptive domain name'))
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

