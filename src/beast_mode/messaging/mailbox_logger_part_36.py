from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def __enter__(self):
    """Context manager entry"""
    self.start()
    return self
