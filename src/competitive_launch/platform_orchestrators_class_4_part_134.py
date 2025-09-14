from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _configure_consistency_guarantees(self) -> Dict[str, Any]:
    """Configure consistency guarantees."""
    return {'level': 'strong', 'guarantees': ['linearizability', 'causal_consistency']}
