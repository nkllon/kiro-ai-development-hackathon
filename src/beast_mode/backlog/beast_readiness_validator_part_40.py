from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def validate_beast_readiness(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate overall Beast Mode system readiness"""
        readiness_rules = ["beast_mode_ready", "interface_registry_ready", "compliance_system_ready", "validation_framework_ready"]
        return self.validate(system_data, readiness_rules)

# Global Beast readiness validator instance
beast_readiness_validator = BeastReadinessValidator()
validation_framework = beast_readiness_validator

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

