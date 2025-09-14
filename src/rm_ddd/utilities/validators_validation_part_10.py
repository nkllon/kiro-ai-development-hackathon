
def validate_domain_model(self, model: Any) -> ValidationResult:
    """Validate any domain model by detecting its type."""
    if isinstance(model, AggregateRoot):
        return self.validate_aggregate(model)
    elif isinstance(model, Entity):
        return self.validate_entity(model)
    elif isinstance(model, DomainService):
        return self.validate_service(model)
    elif isinstance(model, ValueObject):
        return self.validate_value_object(model)
    else:
        result = ValidationResult(is_valid=True)
        result.add_warning(f'Unknown domain model type: {type(model)}')
        return result
