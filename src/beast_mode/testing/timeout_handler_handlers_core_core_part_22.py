
def _estimate_completion_time(self, operation_id: str, current_elapsed: float) -> Optional[float]:
    """Estimate completion time based on historical data"""
    if len(self.timeout_events) < 5:
        return None
    completed_operations = [e for e in self.timeout_events if e.operation_completed]
    if completed_operations:
        avg_completion = sum((e.elapsed_seconds for e in completed_operations)) / len(completed_operations)
        return max(avg_completion, current_elapsed + 5)
    return None
