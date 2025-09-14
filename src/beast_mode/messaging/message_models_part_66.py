from datetime import datetime
from typing import Dict, List, Any

def is_expired(self) -> bool:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Check if message has expired."""
    if not self.expires_at:
        return False
    return datetime.now() > self.expires_at
