from src.rm_ddd.core.health import ModuleHealth

def _validate_service_statelessness(self, service: DomainService) -> ValidationResult:
    """Validate service statelessness."""
    result = ValidationResult(is_valid=True)
    instance_vars = [attr for attr in dir(service) if not attr.startswith('_') and (not callable(getattr(service, attr)))]
    if instance_vars:
        result.add_warning(f'Domain service has instance variables that may indicate state: {instance_vars}')
    return result

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

