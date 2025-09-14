from src.rm_ddd.core.registry import register_module

def _calculate_expected_completion(self, parallel_plan: Dict[str, Any], scope_optimization: Dict[str, Any]) -> datetime:
    """Calculate expected completion time with acceleration."""
    time_savings = parallel_plan.get('expected_time_savings', 0) + scope_optimization.get('time_saved_days', 0)
    days_saved = time_savings * 10
    return datetime.now() + timedelta(days=max(1, 10 - days_saved))
