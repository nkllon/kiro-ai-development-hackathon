from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _extract_affected_components(self, issues: List[ComplianceIssue]) -> List[str]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Extract unique affected components from issues."""
    components = set()
    for issue in issues:
        components.update(issue.affected_files)
    return sorted(list(components))
