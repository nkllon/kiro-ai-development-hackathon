from src.rm_ddd.core.health import ModuleHealth

def validate(self, target: Any) -> ValidationResult:
    """Execute the validation rule."""
    try:
        return self.validator_func(target)
    except Exception as e:
        result = ValidationResult(is_valid=False)
        result.add_error(f"Validation rule '{self.name}' failed: {str(e)}")
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

