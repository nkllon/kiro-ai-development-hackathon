from src.rm_ddd.core.health import ModuleHealth

def validate_required_fields(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    for field in self.required_fields:
        if not hasattr(domain, field) or not getattr(domain, field):
            issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' missing required field: {field}", suggested_fix=f'Add {field} to domain definition'))
    return issues
