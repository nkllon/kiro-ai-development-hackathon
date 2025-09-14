from src.rm_ddd.core.health import ModuleHealth

def validate_file_patterns(self, domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    """Validate domain file patterns"""
    issues = []
    if not domain.patterns:
        issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.PATTERN, description=f"Domain '{domain.name}' has no file patterns", suggested_fix='Add at least one file pattern to define domain scope'))
        return issues
    for pattern in domain.patterns:
        if not isinstance(pattern, str) or not pattern.strip():
            issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.PATTERN, description=f"Invalid pattern in domain '{domain.name}': {pattern}", suggested_fix='Ensure all patterns are non-empty strings'))
            continue
        if pattern.startswith('/'):
            issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.PATTERN, description=f"Pattern '{pattern}' starts with '/' (absolute path)", suggested_fix='Use relative paths for better portability'))
        if '\\' in pattern:
            issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.PATTERN, description=f"Pattern '{pattern}' uses backslashes", suggested_fix='Use forward slashes for cross-platform compatibility'))
        if self.check_filesystem:
            if not self._pattern_has_matches(pattern):
                issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.PATTERN, description=f"Pattern '{pattern}' matches no files", suggested_fix='Verify pattern is correct or files exist'))
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

