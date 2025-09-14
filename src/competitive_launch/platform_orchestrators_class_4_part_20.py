from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _create_implementation_plans(self, specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create implementation plans for generated features."""
        return [{'feature': spec['name'], 'implementation_approach': 'systematic', 'estimated_effort': '2-3 days', 'competitive_advantage': 'high'} for spec in specs]
