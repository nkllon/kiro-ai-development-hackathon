from src.rm_ddd.core.health import ModuleHealth

    def check_pattern_overlaps(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
        issues = []
        domain_patterns = {}
        for domain_name, domain in domains.items():
            domain_patterns[domain_name] = domain.patterns
        for domain1, patterns1 in domain_patterns.items():
            for domain2, patterns2 in domain_patterns.items():
                if domain1 >= domain2:
                    continue
                for pattern1 in patterns1:
                    for pattern2 in patterns2:
                        if self._patterns_overlap(pattern1, pattern2):
                            issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.PATTERN, description=f"Pattern overlap between '{domain1}' and '{domain2}': '{pattern1}' vs '{pattern2}'", suggested_fix='Review domain boundaries to avoid pattern conflicts', affected_files=[domain1, domain2]))
        return issues
    self._consistency_checks.append(ConsistencyCheck(name='pattern_overlaps', description='Check for overlapping file patterns between domains', severity=IssueSeverity.WARNING, checker_func=check_pattern_overlaps))
