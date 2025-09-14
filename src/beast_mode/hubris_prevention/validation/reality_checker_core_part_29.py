from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def add_rule(self, name: str, validator: Callable, error_message: str):
        """Support custom validation rules"""
        rule = ValidationRule(name, validator, error_message)
        self.rules[name] = rule
        return True
    
    # Predefined validation rules