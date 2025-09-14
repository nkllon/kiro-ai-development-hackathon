from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _enable_feature_generation(self, resources: KiroResources) -> Dict[str, Any]:
        """Enable competitive feature generation."""
        return {'enabled': True, 'generation_methods': ['spec_driven', 'market_analysis', 'competitive_intelligence'], 'quality_validation': 'automated'}
