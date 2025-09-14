from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def _wrap_aggregate_methods(cls: Type, max_size: int):
    """Wrap aggregate methods to enforce size limits."""
