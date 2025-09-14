from datetime import datetime
from typing import Dict, List, Any

def _collect_all_issues(self, analysis_result: ComplianceAnalysisResult) -> List[ComplianceIssue]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Collect all issues from all compliance categories."""
    all_issues = []
    all_issues.extend(analysis_result.rdi_compliance.issues)
    all_issues.extend(analysis_result.rm_compliance.issues)
    all_issues.extend(analysis_result.test_coverage_status.issues)
    all_issues.extend(analysis_result.task_completion_reconciliation.issues)
    all_issues.extend(analysis_result.critical_issues)
    unique_issues = []
    seen = set()
    for issue in all_issues:
        key = (issue.description, tuple(sorted(issue.affected_files)))
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)
    return unique_issues
