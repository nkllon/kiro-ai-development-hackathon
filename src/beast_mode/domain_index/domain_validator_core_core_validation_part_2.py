from src.rm_ddd.core.health import ModuleHealth

def check(self, domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
    """Execute consistency check"""
    try:
        return self.checker_func(domains, context) or []
    except Exception as e:
        return [HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f"Consistency check '{self.name}' failed: {str(e)}", suggested_fix='Check consistency check implementation')]
