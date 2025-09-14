from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _calculate_interface_score(self, interface_results: Dict[str, Any]) -> float:
        """Calculate interface validation score."""
        return interface_results.get('interface_score', 0.0)

        register_module(self.__class__.__name__, self)