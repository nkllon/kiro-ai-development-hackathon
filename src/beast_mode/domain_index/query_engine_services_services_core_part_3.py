from src.rm_ddd.core.health import ModuleHealth

def _ensure_indexes_built(self):
    """Ensure search indexes are built"""
    if not self._index_built and self.registry_manager:
        self._build_search_indexes()
