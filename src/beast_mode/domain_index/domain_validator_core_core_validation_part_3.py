from src.rm_ddd.core.health import ModuleHealth

class ValidatedomainClass:
    """Auto-generated class for functions."""

    def validate_domain(self, domain: Domain, context: Optional[Dict[str, Any]]=None) -> ValidationResult:
    """Validate a single domain against all rules"""
    with self._time_operation('validate_domain'):
    self.validations_performed += 1
    context = context or {}
    context['validator'] = self
    all_issues = []
    for rule in self._validation_rules:
    try:
    issues = rule.validate(domain, context)
    all_issues.extend(issues)
    except Exception as e:
    self.logger.error(f"Validation rule '{rule.name}' failed: {e}")
    all_issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f'Validation rule error: {str(e)}', suggested_fix='Check validation rule implementation'))
    errors = [issue for issue in all_issues if issue.severity == IssueSeverity.CRITICAL]
    warnings = [issue for issue in all_issues if issue.severity == IssueSeverity.WARNING]
    suggestions = [issue.suggested_fix for issue in all_issues if issue.severity == IssueSeverity.INFO]
    self.issues_found += len(all_issues)
    return ValidationResult(is_valid=len(errors) == 0, errors=[issue.description for issue in errors], warnings=[issue.description for issue in warnings], suggestions=suggestions)

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

