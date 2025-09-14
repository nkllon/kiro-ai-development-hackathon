from src.rm_ddd.core.health import ModuleHealth

def validate_domain_service_purity(service: DomainService) -> ValidationResult:
    """Validate domain service contains only domain logic."""
    validator = DomainValidator()
    return validator.validate_service(service)
