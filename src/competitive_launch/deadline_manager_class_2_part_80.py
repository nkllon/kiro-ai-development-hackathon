from src.rm_ddd.core.registry import register_module

def _calculate_days_remaining(self) -> int:
    """Calculate days remaining until hackathon deadline."""
    now = datetime.now()
    delta = self.hackathon_deadline - now
    return max(0, delta.days)
