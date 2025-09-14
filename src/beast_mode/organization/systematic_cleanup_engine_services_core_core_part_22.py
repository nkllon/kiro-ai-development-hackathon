
def _calculate_entropy_reduction(self, cleanup_actions: List[Dict[str, Any]]) -> float:
    """Calculate expected entropy reduction from cleanup actions"""
    high_impact_actions = len([a for a in cleanup_actions if a.get('priority') in ['CRITICAL', 'HIGH']])
    total_actions = len(cleanup_actions)
    return min(0.9, high_impact_actions / total_actions * 0.8) if total_actions > 0 else 0.0
