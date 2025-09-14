from src.rm_ddd.core.health import ModuleHealth

def generate_test_specific_systematic_fixes(self, root_causes: List[RootCause]) -> List[SystematicFix]:
    """
        Generate test-specific systematic fixes - Requirements 4.3, 5.1, 5.2, 5.3, 5.4
        """
    test_specific_fixes = []
    for root_cause in root_causes:
        try:
            if root_cause.cause_type in [RootCauseType.TEST_IMPORT_ERROR, RootCauseType.TEST_ASSERTION_FAILURE, RootCauseType.TEST_FIXTURE_ERROR, RootCauseType.TEST_TIMEOUT, RootCauseType.TEST_SETUP_ERROR]:
                fix = self._generate_pytest_specific_fix(root_cause)
                test_specific_fixes.append(fix)
            elif root_cause.cause_type in [RootCauseType.MAKEFILE_ERROR, RootCauseType.BUILD_DEPENDENCY_ERROR]:
                fix = self._generate_makefile_specific_fix(root_cause)
                test_specific_fixes.append(fix)
            elif root_cause.cause_type == RootCauseType.INFRASTRUCTURE_ERROR:
                fix = self._generate_infrastructure_specific_fix(root_cause)
                test_specific_fixes.append(fix)
            self.logger.info(f'Generated test-specific fix for {root_cause.cause_type}')
        except Exception as e:
            self.logger.error(f'Failed to generate test-specific fix for {root_cause.cause_type}: {e}')
    return test_specific_fixes
