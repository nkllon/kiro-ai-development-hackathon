from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _validate_component_classification(self, component_data: Dict[str, Any]) -> ValidationResult:
        """Validate component classification"""
        if 'component_type' in component_data:
            component_type = component_data['component_type']
            # Check for priority-based classification
            if any(specific_type in component_type for specific_type in 
                   ['enhanced_interface_registry', 'proactive_interface_registry']):
                return ValidationResult.PASS
        return ValidationResult.WARNING
    