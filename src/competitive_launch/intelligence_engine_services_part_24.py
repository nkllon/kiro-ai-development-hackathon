from datetime import datetime
from typing import Dict, List, Any

    def _analyze_competitive_threats(self, moves: List[CompetitorMove]) -> List[CompetitiveThreat]:
        """Analyze competitor moves for threats."""
        threats = []
        for move in moves:
            if move.response_urgency.value in ['immediate', 'urgent']:
                threat = CompetitiveThreat(competitor=move.competitor, threat_type=move.move_type, impact_level=move.market_impact, response_urgency=move.response_urgency, market_impact={'description': move.description}, detection_time=datetime.now(), response_deadline=datetime.now() + timedelta(hours=24))
                threats.append(threat)
        return threats
