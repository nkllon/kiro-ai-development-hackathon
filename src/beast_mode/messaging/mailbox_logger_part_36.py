from datetime import datetime
from typing import Dict, List, Any

def __enter__(self):
    """Context manager entry"""
    self.start()
    return self
