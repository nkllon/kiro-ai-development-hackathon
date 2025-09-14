from datetime import datetime
from typing import Dict, List, Any

    def _generate_threat_alerts(self, threats: List[CompetitiveThreat]) -> List[Dict[str, Any]]:
        """Generate alerts for competitive threats."""
        alerts = []
        for threat in threats:
            alert = {'threat_id': f'threat_{threat.competitor}_{threat.threat_type}', 'severity': threat.response_urgency.value, 'description': f'{threat.competitor} {threat.threat_type} detected', 'response_deadline': threat.response_deadline.isoformat(), 'recommended_action': 'generate_differentiation_strategy'}
            alerts.append(alert)
        return alerts
