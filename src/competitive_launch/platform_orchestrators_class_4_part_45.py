from src.rm_ddd.core.registry import register_module

def _configure_tiflash(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Configure TiFlash for analytics workloads."""
    return {'success': True, 'nodes': 2}
