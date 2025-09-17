from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def make_serializable(obj) -> Any:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, Enum):
        return obj.value
    else:
        return obj
