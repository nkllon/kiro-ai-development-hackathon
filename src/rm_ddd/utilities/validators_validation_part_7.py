from src.rm_ddd.core.health import ModuleHealth

def validate_aggregate(self, aggregate: AggregateRoot) -> ValidationResult:
    """Validate an aggregate root."""
    result = ValidationResult(is_valid=True)
    entity_result = self.validate_entity(aggregate)
    result.merge(entity_result)
    for rule in self._rules['aggregate']:
        rule_result = rule.validate(aggregate)
        result.merge(rule_result)
    return result
