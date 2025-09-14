from src.rm_ddd.core.registry import register_module

    def _calculate_adhoc_benefits(self, months: int) -> float:
        """Calculate ad-hoc approach benefits."""
        monthly_benefit = 20000.0
        return monthly_benefit * months
