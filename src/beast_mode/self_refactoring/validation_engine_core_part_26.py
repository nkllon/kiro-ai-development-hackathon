from datetime import datetime
from typing import Dict, List, Any

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
    