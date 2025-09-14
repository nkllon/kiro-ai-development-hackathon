
def _analyze_make_details(self, failure: Failure) -> Dict[str, Any]:
    """Analyze make failure details"""
    return {'error_type': self._get_make_subcategory(failure), 'makefile_exists': Path('Makefile').exists(), 'makefiles_dir_exists': Path('makefiles').exists(), 'error_in_makefile': 'Makefile' in failure.error_message}
