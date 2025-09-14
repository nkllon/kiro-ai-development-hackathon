
def _build_shared_analysis_context(self, failures: List[TestFailureData], common_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build shared context for batch analysis"""
    return {'batch_analysis': True, 'batch_size': len(failures), 'common_patterns': common_patterns, 'failure_types': list(set((f.failure_type for f in failures))), 'affected_files': list(set((f.test_file for f in failures)))}
