
def _generate_next_steps(self, rca_results: List[RCAResult], summary: TestRCASummaryData) -> List[str]:
    """Generate next steps for developers"""
    next_steps = []
    if summary.critical_issues:
        next_steps.append('Address critical issues first:')
        next_steps.extend([f'  - {issue}' for issue in summary.critical_issues[:3]])
    if summary.systematic_fixes_available > 0:
        next_steps.append(f'Apply {summary.systematic_fixes_available} systematic fixes')
    if summary.pattern_matches_found > 0:
        next_steps.append(f'Review {summary.pattern_matches_found} matching prevention patterns')
    if summary.estimated_fix_time_minutes > 0:
        next_steps.append(f'Estimated fix time: {summary.estimated_fix_time_minutes} minutes')
    if not next_steps:
        next_steps = ['Review test failure details', 'Check test environment setup', 'Verify dependencies are installed', 'Run tests individually to isolate issues']
    return next_steps
