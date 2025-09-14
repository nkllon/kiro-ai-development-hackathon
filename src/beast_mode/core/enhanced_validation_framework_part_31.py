from datetime import datetime
from typing import Dict, List, Any

    def add_rule(self, rule: ValidationRule):
        """Add validation rule"""
        self.rules[rule.name] = rule
    