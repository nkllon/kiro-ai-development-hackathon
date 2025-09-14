from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _calculate_deadline_risk(self, critical_path: List[Dict[str, Any]], analysis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate deadline risk based on critical path."""
    days_remaining = self._calculate_days_remaining()
    total_critical_duration = sum((task['duration_days'] for task in critical_path))
    risk_ratio = total_critical_duration / days_remaining if days_remaining > 0 else float('inf')
    if risk_ratio > 1.2:
        risk_level = 'critical'
        acceleration_required = True
    elif risk_ratio > 1.0:
        risk_level = 'high'
        acceleration_required = True
    elif risk_ratio > 0.8:
        risk_level = 'medium'
        acceleration_required = False
    else:
        risk_level = 'low'
        acceleration_required = False
    return {'risk_level': risk_level, 'risk_ratio': risk_ratio, 'acceleration_required': acceleration_required, 'days_remaining': days_remaining, 'critical_duration': total_critical_duration}
