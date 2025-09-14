from src.rm_ddd.core.health import ModuleHealth

def reload_registry(self) -> bool:
    """Reload registry from file"""
    self.logger.info('Reloading domain registry')
    self._registry_loaded = False
    self._clear_cache()
    return self.load_registry()
