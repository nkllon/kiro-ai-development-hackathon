from src.rm_ddd.core.health import ModuleHealth

def _validate_entity_id(self, entity: Entity) -> ValidationResult:
    """Validate entity has a valid ID."""
    result = ValidationResult(is_valid=True)
    if not hasattr(entity, 'id') or entity.id is None:
        result.add_error('Entity must have a non-null ID')
    elif entity.id == '':
        result.add_error('Entity ID cannot be empty string')
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

