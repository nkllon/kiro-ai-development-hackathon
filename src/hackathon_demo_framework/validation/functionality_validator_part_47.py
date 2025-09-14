from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _calculate_interface_score(self, interface_results: Dict[str, Any]) -> float:
    """Calculate interface validation score."""
    return interface_results.get('interface_score', 0.0)
