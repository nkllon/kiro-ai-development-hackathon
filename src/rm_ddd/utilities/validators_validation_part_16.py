from src.rm_ddd.core.health import ModuleHealth

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

