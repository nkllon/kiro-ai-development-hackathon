
def _analyze_pytest_failures(self, failure: Failure) -> Dict[str, Any]:
    """Analyze pytest-specific failures - Requirement 5.1"""
    pytest_analysis = {}
    try:
        if self._is_pytest_failure(failure):
            pytest_analysis['python_issues'] = self._analyze_python_issues(failure)
            pytest_analysis['import_analysis'] = self._analyze_import_issues(failure)
            pytest_analysis['dependency_analysis'] = self._analyze_test_dependencies(failure)
            pytest_analysis['syntax_analysis'] = self._analyze_syntax_issues(failure)
            pytest_analysis['test_structure'] = self._analyze_test_structure(failure)
            pytest_analysis['analysis_confidence'] = 0.9
        else:
            pytest_analysis['applicable'] = False
            pytest_analysis['reason'] = 'Not a pytest failure'
    except Exception as e:
        pytest_analysis['analysis_error'] = str(e)
    return pytest_analysis
