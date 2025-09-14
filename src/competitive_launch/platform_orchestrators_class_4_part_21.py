from src.rm_ddd.core.registry import register_module

    def _estimate_competitive_advantage(self, specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate competitive advantage of generated features."""
        return {'advantage_score': 0.75, 'estimated_days': 5, 'differentiation_strength': 'high'}

        register_module(self.__class__.__name__, self)