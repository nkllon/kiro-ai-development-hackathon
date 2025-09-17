from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def to_json(self) -> str:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Convert to JSON string."""
    return json.dumps(self.to_dict())
