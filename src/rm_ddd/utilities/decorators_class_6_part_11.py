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
