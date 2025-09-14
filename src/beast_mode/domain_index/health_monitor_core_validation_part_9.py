
def validate_dependencies(self, domain_name: Optional[str]=None) -> List[str]:
    """Validate domain dependencies"""
    with self._time_operation('validate_dependencies'):
        try:
            if not self.registry_manager:
                return ['Registry manager not available']
            issues = []
            if domain_name:
                domain = self.registry_manager.get_domain(domain_name)
                dependency_issues = self._check_dependencies(domain)
                issues.extend([issue.description for issue in dependency_issues])
            else:
                all_domains = self.registry_manager.get_all_domains()
                for domain in all_domains.values():
                    dependency_issues = self._check_dependencies(domain)
                    issues.extend([f'{domain.name}: {issue.description}' for issue in dependency_issues])
            return issues
        except Exception as e:
            self._handle_error(e, 'validate_dependencies')
            return [f'Dependency validation failed: {str(e)}']
