
def validate_rules(self, target: Any, rule_names: Optional[List[str]]=None) -> ValidationResult:
    """
        Validate business rules against a target object.
        
        Args:
            target: Object to validate
            rule_names: Specific rules to validate (None for all)
            
        Returns:
            ValidationResult: Validation results
        """
    result = ValidationResult(is_valid=True)
    rules_to_validate = rule_names or list(self._rules.keys())
    sorted_rules = self._sort_rules_by_dependencies(rules_to_validate)
    for rule_name in sorted_rules:
        try:
            rule_func = self._rules[rule_name]
            is_satisfied = rule_func(target)
            if not is_satisfied:
                description = self._rule_descriptions.get(rule_name, 'No description')
                result.add_error(f"Business rule '{rule_name}' violated: {description}")
        except Exception as e:
            result.add_error(f"Error validating rule '{rule_name}': {str(e)}")
    return result
