from src.rm_ddd.core.health import ModuleHealth

def _identify_opportunities(self, trends: List[MarketTrend], alignment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify market opportunities based on trends."""
    opportunities = []
    for trend in trends:
        if trend.alignment_with_systematic > 0.7 and trend.impact_score > 0.6:
            opportunity = {'name': f'Systematic {trend.trend_name}', 'description': f'Leverage systematic approach for {trend.trend_name}', 'market_size': trend.opportunity_size, 'competitive_advantage': trend.alignment_with_systematic, 'implementation_priority': 'high' if trend.impact_score > 0.8 else 'medium'}
            opportunities.append(opportunity)
    return opportunities
