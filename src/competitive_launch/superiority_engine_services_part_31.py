from datetime import datetime
from typing import Dict, List, Any

    def _calculate_systematic_investment(self, months: int) -> float:
        """Calculate systematic approach investment cost."""
        base_cost = 50000.0
        monthly_cost = 10000.0
        return base_cost + monthly_cost * months
