from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _validate_syntax(self, component_data: Dict[str, Any]) -> ValidationResult:
        """Validate Python syntax"""
        if 'code' in component_data:
            try:
                ast.parse(component_data['code'])
                return ValidationResult.PASS
            except SyntaxError:
                return ValidationResult.FAIL
        return ValidationResult.WARNING
    