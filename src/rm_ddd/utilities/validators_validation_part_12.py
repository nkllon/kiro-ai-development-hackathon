
def _validate_entity_context(self, entity: Entity) -> ValidationResult:
    """Validate entity has a domain context."""
    result = ValidationResult(is_valid=True)
    if not hasattr(entity, 'domain_context') or not entity.domain_context:
        result.add_error('Entity must have a domain context')
    return result
