class EnhancedValidationFramework(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Enhanced validation framework with lessons learned"""
    
    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[ValidationReport] = []
        self._initialize_default_rules()
    
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
    
    def add_rule(self, rule: ValidationRule):
        """Add validation rule"""
        self.rules[rule.name] = rule
    
    def validate_component(self, component_name: str, component_data: Dict[str, Any]) -> ValidationReport:
        """Validate a component against all applicable rules"""
        results = []
        passed = 0
        failed = 0
        warnings = 0
        
        for rule_name, rule in self.rules.items():
            try:
                result = rule.validator_func(component_data)
                if result == ValidationResult.PASS:
                    passed += 1
                elif result == ValidationResult.FAIL:
                    failed += 1
                elif result == ValidationResult.WARNING:
                    warnings += 1
                
                results.append({
                    'rule_name': rule_name,
                    'result': result.value,
                    'message': rule.description,
                    'level': rule.level.value
                })
            except Exception as e:
                failed += 1
                results.append({
                    'rule_name': rule_name,
                    'result': ValidationResult.FAIL.value,
                    'message': f"Validation error: {str(e)}",
                    'level': rule.level.value
                })
        
        total_checks = len(self.rules)
        overall_score = (passed / total_checks) * 100 if total_checks > 0 else 0
        
        report = ValidationReport(
            component_name=component_name,
            timestamp=datetime.now(),
            total_checks=total_checks,
            passed=passed,
            failed=failed,
            warnings=warnings,
            results=results,
            overall_score=overall_score
        )
        
        self.validation_history.append(report)
        return report
    
    def _validate_syntax(self, component_data: Dict[str, Any]) -> ValidationResult:
        """Validate Python syntax"""
        if 'code' in component_data:
            try:
                ast.parse(component_data['code'])
                return ValidationResult.PASS
            except SyntaxError:
                return ValidationResult.FAIL
        return ValidationResult.WARNING
    
    def _validate_math_calculations(self, component_data: Dict[str, Any]) -> ValidationResult:
        """Validate mathematical calculations"""
        if 'calculations' in component_data:
            calculations = component_data['calculations']
            for calc in calculations:
                if isinstance(calc, (int, float)) and (calc < 0 or calc > 1000):
                    return ValidationResult.WARNING
        return ValidationResult.PASS
    
    def _validate_component_classification(self, component_data: Dict[str, Any]) -> ValidationResult:
        """Validate component classification"""
        if 'component_type' in component_data:
            component_type = component_data['component_type']
            # Check for priority-based classification
            if any(specific_type in component_type for specific_type in 
                   ['enhanced_interface_registry', 'proactive_interface_registry']):
                return ValidationResult.PASS
        return ValidationResult.WARNING
    
    def _validate_requirements_fidelity(self, component_data: Dict[str, Any]) -> ValidationResult:
        """Validate requirements fidelity scoring"""
        if 'fidelity_score' in component_data:
            score = component_data['fidelity_score']
            if isinstance(score, (int, float)) and 0 <= score <= 100:
                return ValidationResult.PASS
            elif score > 1000:  # Detect inflated scores
                return ValidationResult.FAIL
        return ValidationResult.WARNING
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary"""
        if not self.validation_history:
            return {'message': 'No validation history available'}
        
        total_reports = len(self.validation_history)
        avg_score = sum(report.overall_score for report in self.validation_history) / total_reports
        
        return {
            'total_components_validated': total_reports,
            'average_score': avg_score,
            'last_validation': self.validation_history[-1].timestamp.isoformat(),
            'validation_trend': 'improving' if len(self.validation_history) > 1 and 
                              self.validation_history[-1].overall_score > self.validation_history[-2].overall_score 
                              else 'stable'
        }
    
    def export_validation_report(self, file_path: str):
        """Export validation report to file"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'validation_summary': self.get_validation_summary(),
            'validation_history': [
                {
                    'component_name': report.component_name,
                    'timestamp': report.timestamp.isoformat(),
                    'overall_score': report.overall_score,
                    'results': report.results
                }
                for report in self.validation_history
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2)

# Global instance for easy access
enhanced_validator = EnhancedValidationFramework()
