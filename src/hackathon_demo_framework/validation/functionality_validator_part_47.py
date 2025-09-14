from datetime import datetime
from typing import Dict, List, Any

def _calculate_interface_score(self, interface_results: Dict[str, Any]) -> float:
    """Calculate interface validation score."""
    return interface_results.get('interface_score', 0.0)
