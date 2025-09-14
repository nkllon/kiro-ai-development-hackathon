from src.rm_ddd.core.health import ModuleHealth

def _analyze_test_specific_factors(self, failure: Failure) -> Dict[str, Any]:
    """Analyze test-specific factors for comprehensive analysis"""
    test_analysis = {}
    try:
        is_test_failure = failure.component.startswith('test:') or 'test' in failure.component.lower() or failure.category in [FailureCategory.PYTEST_FAILURE, FailureCategory.MAKE_TARGET_FAILURE, FailureCategory.INFRASTRUCTURE_FAILURE, FailureCategory.TEST_ENVIRONMENT_FAILURE] or self._is_pytest_failure(failure) or self._is_make_failure(failure) or self._is_infrastructure_failure(failure)
        if is_test_failure:
            test_analysis['is_test_failure'] = True
            test_analysis['test_categorization'] = self.analyze_test_failure_categorization(failure)
            if failure.context and 'test_file' in failure.context:
                test_analysis['test_file'] = failure.context['test_file']
                test_analysis['test_function'] = failure.context.get('test_function', 'unknown')
                test_analysis['pytest_node_id'] = failure.context.get('pytest_node_id', 'unknown')
            test_analysis['test_environment'] = self._analyze_test_environment(failure)
        else:
            test_analysis['is_test_failure'] = False
            test_analysis['reason'] = 'Not identified as test-related failure'
    except Exception as e:
        test_analysis['analysis_error'] = str(e)
    return test_analysis
