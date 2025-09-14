from src.rm_ddd.core.health import ModuleHealth

def _validate_service_statelessness(self, service: DomainService) -> ValidationResult:
    """Validate service statelessness."""
    result = ValidationResult(is_valid=True)
    instance_vars = [attr for attr in dir(service) if not attr.startswith('_') and (not callable(getattr(service, attr)))]
    if instance_vars:
        result.add_warning(f'Domain service has instance variables that may indicate state: {instance_vars}')
    return result
