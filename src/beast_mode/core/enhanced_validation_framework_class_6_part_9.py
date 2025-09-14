from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _validate_math_calculations(self, component_data: Dict[str, Any]) -> ValidationResult:
        """Validate mathematical calculations"""
        if 'calculations' in component_data:
            calculations = component_data['calculations']
            for calc in calculations:
                if isinstance(calc, (int, float)) and (calc < 0 or calc > 1000):
                    return ValidationResult.WARNING
        return ValidationResult.PASS
    