
def _create_empty_report(self, reason: str) -> CodeQualityReport:
    """Create an empty report with error information."""
    return CodeQualityReport(overall_score=0.0, complexity_score=0.0, maintainability_score=0.0, documentation_score=0.0, style_score=0.0, security_score=0.0, performance_score=0.0, total_issues=1, critical_issues=1, major_issues=0, minor_issues=0, issues=[CodeQualityIssue(file_path='', line_number=1, issue_type=CodeQualityMetric.MAINTAINABILITY, severity='critical', message=reason, suggestion='Ensure project has analyzable Python source files')], recommendations=[reason], files_analyzed=0, lines_of_code=0)
