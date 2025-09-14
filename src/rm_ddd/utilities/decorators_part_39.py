from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

    def validate_boundaries(self) -> ValidationResult:
        """Validate aggregate boundaries."""
        result = ValidationResult(is_valid=True)
        try:
            if hasattr(self, 'validate_domain_invariants'):
                invariant_result = self.validate_domain_invariants()
                result.merge(invariant_result)
        except Exception as e:
            result.add_error(f'Boundary validation failed: {str(e)}')
        return result
    cls._validate_boundaries = validate_boundaries

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

