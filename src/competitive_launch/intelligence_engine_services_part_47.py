from datetime import datetime
from typing import Dict, List, Any

    def _calculate_threat_level(self, insights: List[str]) -> str:
        """Calculate overall competitive threat level."""
        if any(('immediate response needed' in insight for insight in insights)):
            return 'high'
        elif len(insights) > 2:
            return 'medium'
        else:
            return 'low'
