from src.rm_ddd.core.registry import register_module

    def _calculate_systematic_benefits(self, months: int) -> float:
        """Calculate systematic approach benefits."""
        monthly_benefit = 50000.0
        return monthly_benefit * months
