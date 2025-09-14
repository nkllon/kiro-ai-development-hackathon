
def validate_entity(self, entity: Entity) -> ValidationResult:
    """Validate a domain entity."""
    result = ValidationResult(is_valid=True)
    for rule in self._rules['entity']:
        rule_result = rule.validate(entity)
        result.merge(rule_result)
    for rule in self._rules['general']:
        rule_result = rule.validate(entity)
        result.merge(rule_result)
    return result
