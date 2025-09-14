
def _identify_test_specific_root_causes(self, failure: Failure, analysis: ComprehensiveAnalysisResult) -> List[RootCause]:
    """Identify test-specific root causes"""
    test_root_causes = []
    if self._is_pytest_failure(failure):
        if 'ImportError' in failure.error_message:
            test_root_causes.append(RootCause(cause_type=RootCauseType.TEST_IMPORT_ERROR, description='Test import error - missing or broken test dependencies', evidence=['ImportError in test execution', failure.error_message], confidence_score=0.9, impact_severity='high', affected_components=[failure.component]))
        if 'AssertionError' in failure.error_message:
            test_root_causes.append(RootCause(cause_type=RootCauseType.TEST_ASSERTION_FAILURE, description='Test assertion failure - test logic or implementation issue', evidence=['AssertionError in test execution', failure.error_message], confidence_score=0.8, impact_severity='medium', affected_components=[failure.component]))
        if 'fixture' in failure.error_message.lower():
            test_root_causes.append(RootCause(cause_type=RootCauseType.TEST_FIXTURE_ERROR, description='Test fixture error - fixture setup or teardown issue', evidence=['Fixture error in test execution', failure.error_message], confidence_score=0.8, impact_severity='medium', affected_components=[failure.component]))
    elif self._is_make_failure(failure):
        if 'No rule to make target' in failure.error_message:
            test_root_causes.append(RootCause(cause_type=RootCauseType.MAKEFILE_ERROR, description='Makefile target missing - build system configuration issue', evidence=['Missing make target', failure.error_message], confidence_score=0.9, impact_severity='high', affected_components=['makefile', 'build_system']))
        if 'missing separator' in failure.error_message:
            test_root_causes.append(RootCause(cause_type=RootCauseType.MAKEFILE_ERROR, description='Makefile syntax error - incorrect tab/space formatting', evidence=['Makefile syntax error', failure.error_message], confidence_score=0.9, impact_severity='medium', affected_components=['makefile']))
    elif self._is_infrastructure_failure(failure):
        if 'PermissionError' in failure.error_message:
            test_root_causes.append(RootCause(cause_type=RootCauseType.INFRASTRUCTURE_ERROR, description='Infrastructure permission error - system access issue', evidence=['Permission error in system operation', failure.error_message], confidence_score=0.8, impact_severity='high', affected_components=['system', 'infrastructure']))
    return test_root_causes
