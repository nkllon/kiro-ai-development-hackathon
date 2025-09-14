from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _calculate_integration_score(self, integration_results: Dict[str, Any]) -> float:
    """Calculate integration validation score."""
    return integration_results.get('integration_score', 0.0)
