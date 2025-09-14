from datetime import datetime
from typing import Dict, List, Any

    def _calculate_opportunity_score(self, opportunities: List[Dict[str, Any]]) -> float:
        """Calculate overall market opportunity score."""
        if not opportunities:
            return 0.0
        return sum((opp['competitive_advantage'] for opp in opportunities)) / len(opportunities)
