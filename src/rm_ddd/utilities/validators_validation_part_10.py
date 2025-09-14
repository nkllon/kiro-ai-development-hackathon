from src.rm_ddd.core.health import ModuleHealth

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

