from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _calculate_time_to_market_advantage(self) -> TimeToMarketAdvantage:
        """Calculate time-to-market competitive advantage."""
        return TimeToMarketAdvantage(development_velocity=0.5, deployment_speed=0.6, feature_delivery=0.4, market_response=0.7)
