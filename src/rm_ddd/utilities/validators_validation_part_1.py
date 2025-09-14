from src.rm_ddd.core.health import ModuleHealth

def validate_entity_invariants(entity: Entity) -> ValidationResult:
    """Validate standard entity invariants."""
    validator = DomainValidator()
    return validator.validate_entity(entity)
