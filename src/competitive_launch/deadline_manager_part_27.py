from datetime import datetime
from typing import Dict, List, Any

    def _calculate_days_remaining(self) -> int:
        """Calculate days remaining until hackathon deadline."""
        now = datetime.now()
        delta = self.hackathon_deadline - now
        return max(0, delta.days)
