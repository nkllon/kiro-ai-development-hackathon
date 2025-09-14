from src.rm_ddd.core.health import ModuleHealth

def get_all_modules(self) -> List[RegisteredModule]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Get information about all registered modules."""
    with self._lock:
        return list(self._modules.values())
