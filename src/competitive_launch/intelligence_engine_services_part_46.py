from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _generate_competitive_insights(self, competitor_analysis: Dict[str, Any], trend_analysis: Dict[str, Any], feedback_analysis: Dict[str, Any]) -> List[str]:
        """Generate competitive insights from analysis."""
        insights = []
        if competitor_analysis['high_impact_moves'] > 0:
            insights.append('High-impact competitor moves detected - immediate response needed')
        if trend_analysis['high_alignment_trends'] > 0:
            insights.append('Market trends highly aligned with systematic approach - opportunity to lead')
        if feedback_analysis['positive_sentiment'] > feedback_analysis['total_feedback'] * 0.7:
            insights.append('Strong positive customer sentiment - leverage for competitive advantage')
        return insights
