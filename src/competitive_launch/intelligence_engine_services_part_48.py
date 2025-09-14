from datetime import datetime
from typing import Dict, List, Any

    def _generate_recommended_actions(self, insights: List[str], threat_level: str) -> List[Dict[str, Any]]:
        """Generate recommended actions based on insights and threat level."""
        actions = []
        if threat_level == 'high':
            actions.append({'action': 'Activate emergency competitive response protocols', 'priority': 'immediate', 'timeline': 'within 2 hours'})
        if any(('opportunity to lead' in insight for insight in insights)):
            actions.append({'action': 'Accelerate systematic superiority demonstration', 'priority': 'high', 'timeline': 'within 24 hours'})
        return actions
