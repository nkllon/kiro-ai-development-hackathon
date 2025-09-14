from src.rm_ddd.core.registry import register_module

    def _calculate_adhoc_investment(self, months: int) -> float:
        """Calculate ad-hoc approach investment cost."""
        base_cost = 20000.0
        monthly_cost = 25000.0
        return base_cost + monthly_cost * months
