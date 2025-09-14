from src.rm_ddd.core.health import ModuleHealth

def add_validation_rule(self, rule) -> None:
    """Add custom validation rule"""
    self._validator.add_validation_rule(rule)
