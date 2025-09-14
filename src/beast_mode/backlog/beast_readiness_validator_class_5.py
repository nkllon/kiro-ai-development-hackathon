from src.rm_ddd.core.registry import register_module
class BeastReadinessValidator(ValidationFramework, ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Beast Readiness Validator - Specialized for Beast Mode readiness validation"""
    
    def __init__(self):
        super().__init__()
        self.name = "BeastReadinessValidator"
        self.setup_beast_readiness_rules()
    
    def setup_beast_readiness_rules(self):
        """Setup Beast Mode specific readiness validation rules"""
        self.add_rule("beast_mode_ready", self._check_beast_mode_ready, "Beast Mode system not ready")
        self.add_rule("interface_registry_ready", self._check_interface_registry_ready, "Interface registry not ready")
        self.add_rule("compliance_system_ready", self._check_compliance_system_ready, "Compliance system not ready")
        self.add_rule("validation_framework_ready", self._check_validation_framework_ready, "Validation framework not ready")
    
    def _check_beast_mode_ready(self, system_data: Any) -> bool:
        """Check if Beast Mode system is ready"""
        return system_data is not None and isinstance(system_data, dict)
    
    def _check_interface_registry_ready(self, registry_data: Any) -> bool:
        """Check if interface registry is ready"""
        return registry_data is not None and isinstance(registry_data, dict)
    
    def _check_compliance_system_ready(self, compliance_data: Any) -> bool:
        """Check if compliance system is ready"""
        return compliance_data is not None and isinstance(compliance_data, dict)
    
    def _check_validation_framework_ready(self, validation_data: Any) -> bool:
        """Check if validation framework is ready"""
        return validation_data is not None and isinstance(validation_data, dict)
    
    def validate_beast_readiness(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate overall Beast Mode system readiness"""
        readiness_rules = ["beast_mode_ready", "interface_registry_ready", "compliance_system_ready", "validation_framework_ready"]
        return self.validate(system_data, readiness_rules)

        register_module(self.__class__.__name__, self)
# Global Beast readiness validator instance
beast_readiness_validator = BeastReadinessValidator()
validation_framework = beast_readiness_validator
