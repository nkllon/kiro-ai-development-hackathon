
def validate(self, domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    """Execute validation rule"""
    try:
        return self.validator_func(domain, context) or []
    except Exception as e:
        return [HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f"Validation rule '{self.name}' failed: {str(e)}", suggested_fix='Check validation rule implementation')]
