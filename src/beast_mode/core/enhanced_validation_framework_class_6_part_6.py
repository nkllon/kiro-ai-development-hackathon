from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class AddruleClass:
    """Auto-generated class for functions."""

    def add_rule(self, rule: ValidationRule):
    """Add validation rule"""
    self.rules[rule.name] = rule
