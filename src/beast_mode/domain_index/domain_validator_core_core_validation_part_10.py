
    def check_dependency_consistency(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
        return self.validate_dependencies(domains)
    self._consistency_checks.append(ConsistencyCheck(name='dependency_consistency', description='Check domain dependency consistency', severity=IssueSeverity.CRITICAL, checker_func=check_dependency_consistency))
