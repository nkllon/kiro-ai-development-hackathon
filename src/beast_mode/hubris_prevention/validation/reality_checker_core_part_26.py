from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def validate(self, value: Any, rules: List[str]) -> Dict[str, Any]:
        """Validate input and output data"""
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "validated_at": datetime.now().isoformat()
        }
        
        for rule_name in rules:
            if rule_name in self.rules:
                rule = self.rules[rule_name]
                if not rule.validate(value):
                    results["valid"] = False
                    results["errors"].append(rule.error_message)
            else:
                results["warnings"].append(f"Unknown validation rule: {rule_name}")
        
        self.validation_history.append(results)
        return results

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

    