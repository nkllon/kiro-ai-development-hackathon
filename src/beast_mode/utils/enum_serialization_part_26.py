from datetime import datetime
from typing import Dict, List, Any

def make_enum_json_serializable(*enum_classes: Type[Enum]) -> None:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """
    Convenience function to make multiple enum classes JSON serializable.
    
    Args:
        *enum_classes: Enum classes to make serializable
    """
    for enum_class in enum_classes:
        SerializationHandler.ensure_enum_serializable(enum_class)


# Convenience functions for common use cases