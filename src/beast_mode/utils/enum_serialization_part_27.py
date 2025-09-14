from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def dumps_with_enums(data: Any, **kwargs) -> str:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Shorthand for SerializationHandler.serialize_with_enums"""
    return SerializationHandler.serialize_with_enums(data, **kwargs)

