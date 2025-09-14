from datetime import datetime
from typing import Dict, List, Any

    def _analyze_competitor_move(self, move: CompetitorMove) -> Dict[str, Any]:
        """Analyze a specific competitor move."""
        return {'threat_level': move.response_urgency.value, 'market_impact': move.market_impact, 'our_vulnerability': 0.6, 'response_time_available': 24 if move.response_urgency.value == 'urgent' else 72}
