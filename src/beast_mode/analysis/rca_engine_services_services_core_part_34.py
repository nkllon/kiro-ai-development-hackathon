from src.rm_ddd.core.health import ModuleHealth

def _analyze_python_issues(self, failure: Failure) -> Dict[str, Any]:
    """Analyze Python-specific issues in pytest failures"""
    python_issues = {'syntax_errors': [], 'import_errors': [], 'type_errors': [], 'runtime_errors': []}
    if failure.stack_trace:
        if 'SyntaxError' in failure.stack_trace:
            python_issues['syntax_errors'].append('SyntaxError detected in stack trace')
        if 'ImportError' in failure.stack_trace:
            python_issues['import_errors'].append('ImportError detected in stack trace')
        if 'TypeError' in failure.stack_trace:
            python_issues['type_errors'].append('TypeError detected in stack trace')
        if 'RuntimeError' in failure.stack_trace:
            python_issues['runtime_errors'].append('RuntimeError detected in stack trace')
    return python_issues
