
def _perform_health_check(self, domain: Domain) -> HealthStatus:
    """Perform comprehensive health check for a domain"""
    start_time = time.time()
    issues = []
    pattern_issues = self._check_file_patterns(domain)
    issues.extend(pattern_issues)
    dependency_issues = self._check_dependencies(domain)
    issues.extend(dependency_issues)
    content_issues = self._check_content_indicators(domain)
    issues.extend(content_issues)
    tool_issues = self._check_domain_tools(domain)
    issues.extend(tool_issues)
    if len(issues) > self.max_issues_per_domain:
        issues = issues[:self.max_issues_per_domain]
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f'Too many issues detected (showing first {self.max_issues_per_domain})', suggested_fix='Review domain configuration and resolve critical issues first'))
    metrics = self._calculate_health_metrics(domain, issues)
    status_type = self._determine_health_status_type(issues, metrics)
    self.issues_detected += len(issues)
    check_duration = int((time.time() - start_time) * 1000)
    return HealthStatus(status=status_type, last_check=datetime.now(), issues=issues, metrics=metrics, check_duration_ms=check_duration, next_check=datetime.now() + timedelta(minutes=self.check_interval))
