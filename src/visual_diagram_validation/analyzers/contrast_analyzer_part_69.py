from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def gamma_correct(c):
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    if c <= 0.03928:
        return c / 12.92
    else:
        return math.pow((c + 0.055) / 1.055, 2.4)
