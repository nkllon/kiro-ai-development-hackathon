from datetime import datetime
from typing import Dict, List, Any

def _get_vulnerability_categories(self, findings: List[Finding]) -> List[str]:
    """Get unique vulnerability categories from findings"""
    categories = set()
    for finding in findings:
        vuln_type = finding.evidence.get('vulnerability_type', 'unknown')
        categories.add(vuln_type)
    return list(categories)
