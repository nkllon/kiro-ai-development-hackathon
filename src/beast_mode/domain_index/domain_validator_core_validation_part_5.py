from src.rm_ddd.core.health import ModuleHealth

def check_consistency(self, domains: DomainCollection) -> List[HealthIssue]:
    """Check cross-domain consistency"""
    with self._time_operation('check_consistency'):
        self.consistency_checks_performed += 1
        context = {'validator': self}
        all_issues = []
        for check in self._consistency_checks:
            try:
                issues = check.check(domains, context)
                all_issues.extend(issues)
            except Exception as e:
                self.logger.error(f"Consistency check '{check.name}' failed: {e}")
                all_issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f'Consistency check error: {str(e)}', suggested_fix='Check consistency check implementation'))
        self.issues_found += len(all_issues)
        return all_issues
