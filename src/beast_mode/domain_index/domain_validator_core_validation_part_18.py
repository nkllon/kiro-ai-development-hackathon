
def validate_tools(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    if not domain.tools:
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' has no tools configuration", suggested_fix='Add tools configuration for linting, formatting, etc.'))
        return issues
    if not domain.tools.linter:
        issues.append(HealthIssue(severity=IssueSeverity.INFO, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' has no linter configured", suggested_fix='Configure a linter for code quality'))
    if not domain.tools.formatter:
        issues.append(HealthIssue(severity=IssueSeverity.INFO, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' has no formatter configured", suggested_fix='Configure a formatter for consistent code style'))
    return issues
