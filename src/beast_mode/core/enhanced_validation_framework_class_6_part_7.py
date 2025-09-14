from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


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
    