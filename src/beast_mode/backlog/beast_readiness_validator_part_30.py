from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _setup_default_rules(self):
        """Setup default validation rules"""
        self.add_rule("not_empty", lambda x: x is not None and x != "", "Value cannot be empty")
        self.add_rule("is_string", lambda x: isinstance(x, str), "Value must be a string")
        self.add_rule("is_number", lambda x: isinstance(x, (int, float)), "Value must be a number")
        self.add_rule("is_positive", lambda x: isinstance(x, (int, float)) and x > 0, "Value must be positive")
        self.add_rule("is_valid_name", lambda x: isinstance(x, str) and len(x) > 2 and x[0].isupper(), 
                     "Name must be a string starting with uppercase and longer than 2 characters")
