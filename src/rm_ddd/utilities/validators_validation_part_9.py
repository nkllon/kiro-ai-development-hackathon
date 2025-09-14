from src.rm_ddd.core.health import ModuleHealth

def validate_value_object(self, value_object: ValueObject) -> ValidationResult:
    """Validate a value object."""
    result = ValidationResult(is_valid=True)
    for rule in self._rules['value_object']:
        rule_result = rule.validate(value_object)
        result.merge(rule_result)
    for rule in self._rules['general']:
        rule_result = rule.validate(value_object)
        result.merge(rule_result)
    return result
