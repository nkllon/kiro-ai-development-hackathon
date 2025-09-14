
def _analyze_syntax_issues(self, failure: Failure) -> Dict[str, Any]:
    """Analyze syntax-related issues"""
    syntax_analysis = {}
    if 'SyntaxError' in failure.error_message or (failure.stack_trace and 'SyntaxError' in failure.stack_trace):
        syntax_analysis['has_syntax_error'] = True
        syntax_analysis['syntax_error_details'] = failure.error_message
    else:
        syntax_analysis['has_syntax_error'] = False
    return syntax_analysis
