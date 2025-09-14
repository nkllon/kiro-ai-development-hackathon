
def _generate_systematic_fix(self, root_cause: RootCause) -> SystematicFix:
    """Generate systematic fix for root cause including test-specific fixes"""
    fix_id = f'fix_{root_cause.cause_type.value}_{int(time.time())}'
    if root_cause.cause_type == RootCauseType.TEST_IMPORT_ERROR:
        return self._generate_pytest_specific_fix(root_cause)
    elif root_cause.cause_type == RootCauseType.TEST_ASSERTION_FAILURE:
        return self._generate_pytest_specific_fix(root_cause)
    elif root_cause.cause_type == RootCauseType.TEST_FIXTURE_ERROR:
        return self._generate_pytest_specific_fix(root_cause)
    elif root_cause.cause_type == RootCauseType.TEST_TIMEOUT:
        return self._generate_pytest_specific_fix(root_cause)
    elif root_cause.cause_type == RootCauseType.TEST_SETUP_ERROR:
        return self._generate_pytest_specific_fix(root_cause)
    elif root_cause.cause_type == RootCauseType.MAKEFILE_ERROR:
        return self._generate_makefile_specific_fix(root_cause)
    elif root_cause.cause_type == RootCauseType.BUILD_DEPENDENCY_ERROR:
        return self._generate_makefile_specific_fix(root_cause)
    elif root_cause.cause_type == RootCauseType.INFRASTRUCTURE_ERROR:
        return self._generate_infrastructure_specific_fix(root_cause)
    elif root_cause.cause_type == RootCauseType.MISSING_FILES:
        return SystematicFix(fix_id=fix_id, root_cause=root_cause, fix_description='Create complete modular Makefile system with all required modules', implementation_steps=['Create makefiles/ directory', 'Generate all required .mk module files (config.mk, platform.mk, colors.mk, etc.)', 'Populate each module with proper content and targets', 'Update main Makefile to include all modules', 'Validate all make targets work correctly'], validation_criteria=['makefiles/ directory exists', 'All required .mk files present', 'make help command succeeds', 'All make targets execute without errors'], rollback_plan='Remove makefiles/ directory and restore original Makefile', estimated_time_minutes=15)
    elif root_cause.cause_type == RootCauseType.PERMISSION_DENIED:
        return SystematicFix(fix_id=fix_id, root_cause=root_cause, fix_description='Fix file permissions systematically', implementation_steps=['Identify files with incorrect permissions', 'Apply correct permissions using chmod', 'Verify user has necessary access rights'], validation_criteria=['File permissions are correct', 'User can access required files', 'Original error no longer occurs'], rollback_plan='Restore original file permissions', estimated_time_minutes=5)
    else:
        return SystematicFix(fix_id=fix_id, root_cause=root_cause, fix_description=f'Generic systematic fix for {root_cause.cause_type.value}', implementation_steps=[f'Analyze {root_cause.cause_type.value} systematically', 'Implement root cause fix', 'Validate fix addresses root cause'], validation_criteria=['Root cause no longer present', 'Original symptoms resolved'], rollback_plan='Revert changes if fix fails', estimated_time_minutes=10)
