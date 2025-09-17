from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def setup_beast_readiness_rules(self):
        """Setup Beast Mode specific readiness validation rules"""
        self.add_rule("beast_mode_ready", self._check_beast_mode_ready, "Beast Mode system not ready")
        self.add_rule("interface_registry_ready", self._check_interface_registry_ready, "Interface registry not ready")
        self.add_rule("compliance_system_ready", self._check_compliance_system_ready, "Compliance system not ready")
        self.add_rule("validation_framework_ready", self._check_validation_framework_ready, "Validation framework not ready")

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

    