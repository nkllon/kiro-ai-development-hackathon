from src.rm_ddd.core.health import ModuleHealth

def set_registry_manager(self, registry_manager):
    """Set the registry manager (dependency injection)"""
    self.registry_manager = registry_manager
    self._index_built = False
