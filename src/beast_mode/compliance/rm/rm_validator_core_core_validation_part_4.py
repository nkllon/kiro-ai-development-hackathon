from src.rm_ddd.core.health import ModuleHealth


class CheckregistryintegrationClass:
    """Auto-generated class for functions."""

    def check_registry_integration(self, module_path: str) -> RegistryIntegrationResult:
    """
    Check proper registry integration for RM components.

    Args:
    module_path: Path to the Python module to validate

    Returns:
    RegistryIntegrationResult with validation details
    """
    issues = []
    try:
    with open(module_path, 'r', encoding='utf-8') as f:
    source_code = f.read()
    has_registration_method = 'register_rm_documentation' in source_code
    has_registry_imports = any((pattern in source_code for pattern in ['DocumentManagementRM', 'from beast_mode.documentation', 'import.*registry']))
    properly_registered = has_registration_method and has_registry_imports
    if not has_registration_method:
    issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.MEDIUM, description='No registry registration method found', affected_files=[module_path], remediation_steps=['Implement register_rm_documentation method', 'Call registration method during module initialization'], blocking_merge=False))
    if not has_registry_imports:
    issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.LOW, description='No registry-related imports found', affected_files=[module_path], remediation_steps=['Import necessary registry components', 'Add DocumentManagementRM import if using documentation registry'], blocking_merge=False))
    registry_compliance_score = 1.0
    if not has_registration_method:
    registry_compliance_score -= 0.6
    if not has_registry_imports:
    registry_compliance_score -= 0.4
    registry_compliance_score = max(0.0, registry_compliance_score)
    return RegistryIntegrationResult(module_path=module_path, properly_registered=properly_registered, registration_method_present=has_registration_method, registry_compliance_score=registry_compliance_score, issues=issues)
    except Exception as e:
    issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.HIGH, description=f'Failed to check registry integration: {str(e)}', affected_files=[module_path], remediation_steps=['Fix file access issues', 'Ensure module file is readable'], blocking_merge=True))
    return RegistryIntegrationResult(module_path=module_path, properly_registered=False, registration_method_present=False, registry_compliance_score=0.0, issues=issues)

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

