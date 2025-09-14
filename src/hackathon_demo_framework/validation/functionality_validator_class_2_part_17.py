from src.rm_ddd.core.registry import register_module

    def _calculate_integration_score(self, integration_results: Dict[str, Any]) -> float:
        """Calculate integration validation score."""
        return integration_results.get('integration_score', 0.0)
