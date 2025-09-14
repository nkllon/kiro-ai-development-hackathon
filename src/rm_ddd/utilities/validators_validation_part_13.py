from src.rm_ddd.core.health import ModuleHealth

def _validate_aggregate_size(self, aggregate: AggregateRoot) -> ValidationResult:
    """Validate aggregate size limits."""
    result = ValidationResult(is_valid=True)
    max_size = getattr(aggregate.__class__, '_max_aggregate_size', 100)
    current_size = self._count_aggregate_members(aggregate)
    if current_size > max_size:
        result.add_warning(f'Aggregate size ({current_size}) exceeds recommended limit ({max_size})')
    return result
