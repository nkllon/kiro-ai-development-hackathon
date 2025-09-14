
def _analyze_makefile_failures(self, failure: Failure) -> Dict[str, Any]:
    """Analyze Makefile-specific failures - Requirement 5.2"""
    makefile_analysis = {}
    try:
        if self._is_make_failure(failure):
            makefile_analysis['makefile_issues'] = self._analyze_makefile_issues(failure)
            makefile_analysis['missing_files'] = self._analyze_missing_files(failure)
            makefile_analysis['build_dependencies'] = self._analyze_build_dependencies(failure)
            makefile_analysis['target_analysis'] = self._analyze_make_targets(failure)
            makefile_analysis['analysis_confidence'] = 0.8
        else:
            makefile_analysis['applicable'] = False
            makefile_analysis['reason'] = 'Not a Makefile failure'
    except Exception as e:
        makefile_analysis['analysis_error'] = str(e)
    return makefile_analysis
