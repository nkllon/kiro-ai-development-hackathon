
def _analyze_test_structure(self, failure: Failure) -> Dict[str, Any]:
    """Analyze test structure issues"""
    structure_analysis = {}
    if failure.context and 'test_file' in failure.context:
        test_file = failure.context['test_file']
        structure_analysis['test_file_exists'] = Path(test_file).exists()
        structure_analysis['test_file_path'] = test_file
        structure_analysis['follows_naming_convention'] = test_file.startswith('test_') or test_file.endswith('_test.py')
    return structure_analysis
