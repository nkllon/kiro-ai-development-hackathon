from src.rm_ddd.core.health import ModuleHealth

class CheckarchitecturalpatternsClass:
    """Auto-generated class for functions."""

    def _check_architectural_patterns(self, module_path: str, complexity_indicators: Dict[str, Any], issues: List[ComplianceIssue]) -> None:
    """Check for specific architectural patterns and violations."""
    try:
    with open(module_path, 'r', encoding='utf-8') as f:
    source_code = f.read()
    class_count = complexity_indicators.get('class_count', 0)
    if class_count > 5:
    issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.HIGH, description=f'Too many classes in module: {class_count} (recommended: ≤5)', affected_files=[module_path], remediation_steps=['Split module into multiple focused modules', 'Group related classes into separate modules', 'Consider using composition over multiple classes'], blocking_merge=False))
    import_count = complexity_indicators.get('import_count', 0)
    if import_count > 20:
    issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.MEDIUM, description=f'Too many imports: {import_count} (recommended: ≤20)', affected_files=[module_path], remediation_steps=['Reduce dependencies by removing unused imports', 'Consider dependency injection to reduce coupling', 'Split module to reduce external dependencies'], blocking_merge=False))
    max_nesting = complexity_indicators.get('max_nesting_depth', 0)
    if max_nesting > 4:
    issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.MEDIUM, description=f'Deep nesting detected: {max_nesting} levels (recommended: ≤4)', affected_files=[module_path], remediation_steps=['Refactor nested conditions using early returns', 'Extract complex logic into separate methods', 'Use guard clauses to reduce nesting'], blocking_merge=False))
    function_count = complexity_indicators.get('function_count', 0)
    if function_count > 25:
    issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.HIGH, description=f'Too many methods: {function_count} (recommended: ≤25)', affected_files=[module_path], remediation_steps=['Split large classes into smaller, focused classes', 'Extract utility methods to separate modules', 'Apply single responsibility principle more strictly'], blocking_merge=False))
    if '"""' not in source_code and "'''" not in source_code:
    issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.LOW, description='No module-level docstring found', affected_files=[module_path], remediation_steps=['Add module-level docstring describing purpose', 'Document all public classes and methods', 'Follow PEP 257 docstring conventions'], blocking_merge=False))
    except Exception as e:
    issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.LOW, description=f'Could not perform architectural pattern analysis: {str(e)}', affected_files=[module_path], remediation_steps=['Ensure module is syntactically valid', 'Check file permissions and accessibility'], blocking_merge=False))

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

