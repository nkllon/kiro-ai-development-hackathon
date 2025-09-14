from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def add_rule(self, rule: ValidationRule):
        """Add validation rule"""
        self.rules[rule.name] = rule
    