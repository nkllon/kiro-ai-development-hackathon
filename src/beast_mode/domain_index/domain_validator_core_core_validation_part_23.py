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

