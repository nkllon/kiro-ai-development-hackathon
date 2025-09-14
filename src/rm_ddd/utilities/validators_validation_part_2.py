from src.rm_ddd.core.health import ModuleHealth

def validate_aggregate_boundaries(aggregate: AggregateRoot) -> ValidationResult:
    """Validate aggregate boundary rules."""
    validator = DomainValidator()
    return validator.validate_aggregate(aggregate)
