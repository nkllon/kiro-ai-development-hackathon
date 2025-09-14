
def _generate_emergency_report(self, test_failures: List[Any], error_message: str) -> Any:
    """Generate emergency report when fallback fails"""
    from .rca_integration import TestRCAReportData, TestRCASummaryData
    return TestRCAReportData(analysis_timestamp=datetime.now(), total_failures=len(test_failures), failures_analyzed=0, grouped_failures={}, rca_results=[], summary=TestRCASummaryData(most_common_root_causes=[], systematic_fixes_available=0, pattern_matches_found=0, estimated_fix_time_minutes=0, confidence_score=0.0, critical_issues=[f'Emergency: {error_message}']), recommendations=[f'Emergency situation: {error_message}'], prevention_patterns=[], next_steps=['Contact system administrator immediately'])
