from src.rm_ddd.core.health import ModuleHealth

def _load_current_connection(self) -> None:
    """Load current project connection if it exists."""
    try:
        self._current_connection = self.config_manager.load_connection(self.project_root)
    except Exception:
        self._current_connection = None
