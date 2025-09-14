from src.rm_ddd.core.health import ModuleHealth

def get_available_capabilities(self) -> List[str]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Get list of all available capabilities in the system."""
    with self._lock:
        return list(self._capabilities.keys())
