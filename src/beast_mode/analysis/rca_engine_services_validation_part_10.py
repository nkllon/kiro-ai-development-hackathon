from src.rm_ddd.core.health import ModuleHealth

def _analyze_pytest_details(self, failure: Failure) -> Dict[str, Any]:
    """Analyze pytest failure details"""
    return {'error_type': self._get_pytest_subcategory(failure), 'has_stack_trace': failure.stack_trace is not None, 'test_context_available': bool(failure.context.get('test_file')), 'pytest_node_available': bool(failure.context.get('pytest_node_id'))}
