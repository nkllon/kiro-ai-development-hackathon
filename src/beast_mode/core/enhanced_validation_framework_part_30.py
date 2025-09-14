from datetime import datetime
from typing import Dict, List, Any

    def _initialize_default_rules(self):
        """Initialize default validation rules based on lessons learned"""
        
        # Syntax validation rule (prevents cascade failures)
        self.add_rule(ValidationRule(
            name="syntax_validation",
            description="Validate Python syntax before processing",
            level=ValidationLevel.CRITICAL,
            validator_func=self._validate_syntax,
            error_message="Syntax error detected",
            fix_suggestion="Fix syntax errors before proceeding"
        ))
        
        # Math calculation validation rule
        self.add_rule(ValidationRule(
            name="math_calculation_validation",
            description="Validate mathematical calculations",
            level=ValidationLevel.HIGH,
            validator_func=self._validate_math_calculations,
            error_message="Invalid mathematical calculation",
            fix_suggestion="Ensure proper percentage calculation"
        ))
        
        # Component classification validation rule
        self.add_rule(ValidationRule(
            name="component_classification_validation",
            description="Validate component classification accuracy",
            level=ValidationLevel.MEDIUM,
            validator_func=self._validate_component_classification,
            error_message="Component classification mismatch",
            fix_suggestion="Use priority-based classification"
        ))
        
        # Requirements fidelity validation rule
        self.add_rule(ValidationRule(
            name="requirements_fidelity_validation",
            description="Validate requirements fidelity scoring",
            level=ValidationLevel.HIGH,
            validator_func=self._validate_requirements_fidelity,
            error_message="Requirements fidelity scoring error",
            fix_suggestion="Apply proper percentage calculation"
        ))
    