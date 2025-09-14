
def _generate_rca_summary(self, rca_results: List[RCAResult], pattern_matches: List[PreventionPattern]) -> TestRCASummaryData:
    """Generate summary of RCA analysis results"""
    root_cause_counts = {}
    total_fixes = 0
    total_time = 0
    confidence_scores = []
    critical_issues = []
    for result in rca_results:
        for root_cause in result.root_causes:
            cause_type = root_cause.cause_type
            root_cause_counts[cause_type] = root_cause_counts.get(cause_type, 0) + 1
            if root_cause.impact_severity == 'critical':
                critical_issues.append(root_cause.description)
        total_fixes += len(result.systematic_fixes)
        total_time += result.total_analysis_time_seconds
        confidence_scores.append(result.rca_confidence_score)
    most_common = sorted(root_cause_counts.items(), key=lambda x: x[1], reverse=True)
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    estimated_time = total_fixes * 10
    return TestRCASummaryData(most_common_root_causes=most_common, systematic_fixes_available=total_fixes, pattern_matches_found=len(pattern_matches), estimated_fix_time_minutes=estimated_time, confidence_score=avg_confidence, critical_issues=critical_issues)
