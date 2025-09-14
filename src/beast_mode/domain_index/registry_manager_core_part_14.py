from src.rm_ddd.core.health import ModuleHealth

def _warm_cache(self) -> None:
    """Warm cache with frequently accessed domains"""
    try:
        domain_names = list(self._domains.keys())
