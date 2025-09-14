
def _analyze_competitor_moves(self, moves: List[CompetitorMove]) -> Dict[str, Any]:
    """Analyze competitor moves for patterns and threats."""
    return {'total_moves': len(moves), 'high_impact_moves': len([m for m in moves if m.market_impact > 0.7]), 'urgent_responses_needed': len([m for m in moves if m.response_urgency.value == 'urgent']), 'primary_competitor': max(set((m.competitor for m in moves)), key=lambda x: sum((1 for m in moves if m.competitor == x)))}
