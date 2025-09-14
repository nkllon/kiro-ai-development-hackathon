
def generate_comprehensive_report(self, original_failures: List[TestFailureData], grouped_failures: Dict[str, List[TestFailureData]], rca_results: List[RCAResult], pattern_matches: List[PreventionPattern]) -> TestRCAReportData:
    """
        Generate comprehensive RCA report for test failures
        Requirements: 2.2, 2.3, 2.4 - Detailed reporting with actionable recommendations
        """
    try:
        summary = self._generate_rca_summary(rca_results, pattern_matches)
        recommendations = self._generate_recommendations(rca_results)
        all_prevention_patterns = []
        for result in rca_results:
            all_prevention_patterns.extend(result.prevention_patterns)
        all_prevention_patterns.extend(pattern_matches)
        next_steps = self._generate_next_steps(rca_results, summary)
        return TestRCAReportData(analysis_timestamp=datetime.now(), total_failures=len(original_failures), failures_analyzed=len(rca_results), grouped_failures=grouped_failures, rca_results=rca_results, summary=summary, recommendations=recommendations, prevention_patterns=all_prevention_patterns, next_steps=next_steps)
    except Exception as e:
        self.logger.error(f'Report generation failed: {e}')
        return TestRCAReportData(analysis_timestamp=datetime.now(), total_failures=len(original_failures), failures_analyzed=0, grouped_failures=grouped_failures, rca_results=rca_results, summary=TestRCASummaryData([], 0, 0, 0, 0.0, [f'Report generation failed: {e}']), recommendations=[f'Report generation failed: {e}'], prevention_patterns=[], next_steps=['Check report generation system', 'Retry with simplified parameters'])
