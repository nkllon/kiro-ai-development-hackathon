
def _validate_entity_id(self, entity: Entity) -> ValidationResult:
    """Validate entity has a valid ID."""
    result = ValidationResult(is_valid=True)
    if not hasattr(entity, 'id') or entity.id is None:
        result.add_error('Entity must have a non-null ID')
    elif entity.id == '':
        result.add_error('Entity ID cannot be empty string')
    return result
