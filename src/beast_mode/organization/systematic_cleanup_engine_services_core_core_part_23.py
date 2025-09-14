
def _estimate_cleanup_time(self, cleanup_actions: List[Dict[str, Any]]) -> str:
    """Estimate time required for systematic cleanup"""
    action_count = len(cleanup_actions)
    if action_count > 20:
        return '2-3 hours'
    elif action_count > 10:
        return '1-2 hours'
    elif action_count > 5:
        return '30-60 minutes'
    else:
        return '15-30 minutes'
