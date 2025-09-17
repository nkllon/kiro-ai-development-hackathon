from src.rm_ddd.core.health import ModuleHealth

def validate_root_cause_addressed(self, fix: SystematicFix, original_failure: Failure) -> ValidationResult:
    """
        Validate fixes address root cause, not just symptoms (R7.4)
        Required by R7.4: Validate fixes address root cause, not just symptoms
        """
    try:
        self.logger.info(f'Validating systematic fix: {fix.fix_id}')
        validation_evidence = []
        symptoms_resolved = []
        remaining_issues = []
        for criteria in fix.validation_criteria:
            try:
                validation_result = self._execute_validation_criteria(criteria, original_failure)
                validation_evidence.append(f"Criteria '{criteria}': {validation_result['status']}")
                if validation_result['status'] == 'passed':
                    symptoms_resolved.extend(validation_result.get('resolved_symptoms', []))
                else:
                    remaining_issues.extend(validation_result.get('remaining_issues', []))
            except Exception as e:
                validation_evidence.append(f"Criteria '{criteria}': failed - {e}")
                remaining_issues.append(f'Validation failed: {e}')
        fix_successful = len(remaining_issues) == 0
        root_cause_addressed = fix_successful and len(symptoms_resolved) > 0
        confidence_score = len(symptoms_resolved) / max(1, len(symptoms_resolved) + len(remaining_issues))
        return ValidationResult(fix_successful=fix_successful, root_cause_addressed=root_cause_addressed, symptoms_resolved=symptoms_resolved, remaining_issues=remaining_issues, validation_evidence=validation_evidence, confidence_score=confidence_score)
    except Exception as e:
        self.logger.error(f'Fix validation failed: {e}')
        return ValidationResult(fix_successful=False, root_cause_addressed=False, symptoms_resolved=[], remaining_issues=[f'Validation error: {e}'], validation_evidence=[f'Validation failed: {e}'], confidence_score=0.0)

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

