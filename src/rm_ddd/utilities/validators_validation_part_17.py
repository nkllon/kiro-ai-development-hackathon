
def validate_invariants(self, target: Any, invariant_names: Optional[List[str]]=None) -> ValidationResult:
    """
        Validate domain invariants against a target object.
        
        Args:
            target: Object to validate
            invariant_names: Specific invariants to validate (None for all)
            
        Returns:
            ValidationResult: Validation results
        """
    result = ValidationResult(is_valid=True)
    invariants_to_validate = invariant_names or list(self._invariants.keys())
    for invariant_name in invariants_to_validate:
        try:
            invariant_info = self._invariants[invariant_name]
            expression = invariant_info['expression']
            description = invariant_info['description']
            is_satisfied = self._evaluate_invariant(target, expression, invariant_info['context'])
            if not is_satisfied:
                result.add_error(f"Domain invariant '{invariant_name}' violated: {description}")
        except Exception as e:
            result.add_error(f"Error validating invariant '{invariant_name}': {str(e)}")
    return result
