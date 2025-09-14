"""
Validation Framework - Requirements-Driven Implementation
=======================================================
Generated from requirements: Validate input and output data, Support type checking and validation, Provide error reporting and handling, Support custom validation rules
"""

from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ValidationError(Exception):
    """Validation error exception"""
    pass

class ValidationRule:
    """Validation rule definition"""
    
    def __init__(self, name: str, validator: Callable, error_message: str):
        self.name = name
        self.validator = validator
        self.error_message = error_message
    
    def validate(self, value: Any) -> bool:
        """Validate value against rule"""
        try:
            return bool(self.validator(value))
        except Exception:
            return False

class ValidationFramework:
    """Validation Framework - Requirements-Driven Implementation"""
    
    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[Dict[str, Any]] = []
    
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
    
    def check_type(self, value: Any, expected_type: type) -> bool:
        """Support type checking and validation"""
        return isinstance(value, expected_type)
    
    def report_error(self, error: str, context: Optional[Dict[str, Any]] = None):
        """Provide error reporting and handling"""
        error_report = {
            "error": error,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"Validation Error: {error}")
        if context:
            print(f"Context: {context}")
        
        return error_report
    
    def add_rule(self, name: str, validator: Callable, error_message: str):
        """Support custom validation rules"""
        rule = ValidationRule(name, validator, error_message)
        self.rules[name] = rule
        return True
    
    # Predefined validation rules
    def _setup_default_rules(self):
        """Setup default validation rules"""
        self.add_rule("not_empty", lambda x: x is not None and x != "", "Value cannot be empty")
        self.add_rule("is_string", lambda x: isinstance(x, str), "Value must be a string")
        self.add_rule("is_number", lambda x: isinstance(x, (int, float)), "Value must be a number")
        self.add_rule("is_positive", lambda x: isinstance(x, (int, float)) and x > 0, "Value must be positive")
        self.add_rule("is_valid_name", lambda x: isinstance(x, str) and len(x) > 2 and x[0].isupper(), 
                     "Name must be a string starting with uppercase and longer than 2 characters")

# Global validation framework instance
validation_framework = ValidationFramework()
validation_framework._setup_default_rules()
