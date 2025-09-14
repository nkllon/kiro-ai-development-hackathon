from src.rm_ddd.core.health import ModuleHealth

def validate(self, domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    """Execute validation rule"""
    try:
        return self.validator_func(domain, context) or []
    except Exception as e:
        return [HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f"Validation rule '{self.name}' failed: {str(e)}", suggested_fix='Check validation rule implementation')]

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

