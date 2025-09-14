from src.rm_ddd.core.health import ModuleHealth

def analyze_systematic_failure(self, failure_context: Dict[str, Any], systematic_constraints: bool=True) -> Dict[str, Any]:
    """Legacy method - converts to new RCA format"""
    failure = Failure(failure_id=f'legacy_{int(time.time())}', timestamp=datetime.now(), component=failure_context.get('component', 'unknown'), error_message=failure_context.get('error_message', ''), stack_trace=failure_context.get('stack_trace'), context=failure_context, category=FailureCategory.UNKNOWN)
    rca_result = self.perform_systematic_rca(failure)
    return {'root_causes': [rc.description for rc in rca_result.root_causes], 'systematic_analysis': systematic_constraints, 'confidence_score': rca_result.rca_confidence_score, 'recommendations': [fix.fix_description for fix in rca_result.systematic_fixes], 'failure_context': failure_context, 'analysis_time_seconds': rca_result.total_analysis_time_seconds, 'prevention_patterns': len(rca_result.prevention_patterns)}
