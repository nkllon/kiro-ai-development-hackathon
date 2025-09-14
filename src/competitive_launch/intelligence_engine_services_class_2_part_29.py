from src.rm_ddd.core.registry import register_module

    def _determine_competitive_position(self, advantage: float) -> str:
        """Determine competitive position based on advantage score."""
        if advantage >= 0.8:
            return 'market_leader'
        elif advantage >= 0.6:
            return 'strong_competitor'
        elif advantage >= 0.4:
            return 'competitive'
        else:
            return 'behind_competitors'
