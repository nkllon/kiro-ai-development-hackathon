
def _analyze_makefile_issues(self, failure: Failure) -> Dict[str, Any]:
    """Analyze Makefile-specific issues"""
    makefile_issues = {}
    try:
        makefile_issues['makefile_exists'] = Path('Makefile').exists()
        makefile_issues['makefiles_dir_exists'] = Path('makefiles').exists()
        if 'missing separator' in failure.error_message:
            makefile_issues['syntax_error'] = True
            makefile_issues['syntax_details'] = 'Missing tab separator in Makefile'
        if 'No rule to make target' in failure.error_message:
            makefile_issues['missing_target'] = True
            makefile_issues['target_details'] = failure.error_message
    except Exception as e:
        makefile_issues['analysis_error'] = str(e)
    return makefile_issues
