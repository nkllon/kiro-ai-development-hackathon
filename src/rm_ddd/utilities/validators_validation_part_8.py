
def validate_service(self, service: DomainService) -> ValidationResult:
    """Validate a domain service."""
    result = ValidationResult(is_valid=True)
    for rule in self._rules['service']:
        rule_result = rule.validate(service)
        result.merge(rule_result)
    for rule in self._rules['general']:
        rule_result = rule.validate(service)
        result.merge(rule_result)
    return result
