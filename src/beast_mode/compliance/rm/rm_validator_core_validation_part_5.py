from src.rm_ddd.core.health import ModuleHealth

class ValidatermcomplianceClass:
    """Auto-generated class for functions."""

    def validate_rm_compliance(self, module_path: str) -> RMComplianceStatus:
    """
    Perform comprehensive RM compliance validation.

    Args:
    module_path: Path to the Python module to validate

    Returns:
    RMComplianceStatus with overall compliance assessment
    """
    interface_result = self.validate_rm_interface_implementation(module_path)
    size_result = self.check_size_constraints(module_path)
    health_result = self.validate_health_monitoring(module_path)
    registry_result = self.check_registry_integration(module_path)
    all_issues = []
    all_issues.extend(interface_result.issues)
    all_issues.extend(size_result.issues)
    all_issues.extend(health_result.issues)
    all_issues.extend(registry_result.issues)
    scores = [interface_result.interface_compliance_score, 1.0 if size_result.meets_size_constraint else 0.0, health_result.health_monitoring_score, registry_result.registry_compliance_score]
    overall_score = sum(scores) / len(scores) if scores else 0.0
    return RMComplianceStatus(interface_implemented=interface_result.implements_rm_interface, size_constraints_met=size_result.meets_size_constraint, health_monitoring_present=health_result.has_health_monitoring, registry_integrated=registry_result.properly_registered, compliance_score=overall_score, issues=all_issues)

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

