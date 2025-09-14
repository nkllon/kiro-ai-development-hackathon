from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _configure_tiflash(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Configure TiFlash for analytics workloads."""
    return {'success': True, 'nodes': 2}
