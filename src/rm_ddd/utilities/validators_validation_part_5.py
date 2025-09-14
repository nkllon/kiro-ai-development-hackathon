from src.rm_ddd.core.health import ModuleHealth

def validate(self, target: Any) -> ValidationResult:
    """Execute the validation rule."""
    try:
        return self.validator_func(target)
    except Exception as e:
        result = ValidationResult(is_valid=False)
        result.add_error(f"Validation rule '{self.name}' failed: {str(e)}")
        return result
