from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def to_dict(self) -> Dict[str, Any]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Convert to dictionary."""
    result = {}
    for key, value in self.__dict__.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, Enum):
            result[key] = value.value
        elif isinstance(value, list) and value and isinstance(value[0], Enum):
            result[key] = [item.value for item in value]
        else:
            result[key] = value
    return result
