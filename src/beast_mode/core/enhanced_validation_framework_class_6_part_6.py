from src.rm_ddd.core.registry import register_module

    def add_rule(self, rule: ValidationRule):
        """Add validation rule"""
        self.rules[rule.name] = rule
    