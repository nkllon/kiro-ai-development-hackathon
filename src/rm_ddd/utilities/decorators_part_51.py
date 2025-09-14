from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

    def validate_significance(self) -> ValidationResult:
        """Validate that event represents significant business occurrence."""
        result = ValidationResult(is_valid=True)
        try:
            event_data = self.get_event_data()
            if not event_data:
                result.add_warning('Event has no data - may not be significant')
        except Exception as e:
            result.add_error(f'Cannot validate event significance: {str(e)}')
        return result
    cls._validate_significance = validate_significance
