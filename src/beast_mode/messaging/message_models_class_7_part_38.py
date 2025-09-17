from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def get_age_seconds(self) -> float:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Get message age in seconds."""
    return (datetime.now() - self.timestamp).total_seconds()
