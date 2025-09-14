from datetime import datetime
from typing import Dict, List, Any

    def _analyze_market_trends(self, trends: List[MarketTrend]) -> Dict[str, Any]:
        """Analyze market trends for opportunities."""
        return {'total_trends': len(trends), 'high_impact_trends': len([t for t in trends if t.impact_score > 0.7]), 'high_alignment_trends': len([t for t in trends if t.alignment_with_systematic > 0.8]), 'average_opportunity_size': sum((1 for t in trends if t.opportunity_size == 'large')) / len(trends) if trends else 0}
