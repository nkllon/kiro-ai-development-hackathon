from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def default(self, obj: Any) -> Any:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Convert enum objects to their values for JSON serialization."""
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)

