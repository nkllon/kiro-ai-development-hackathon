from datetime import datetime
from typing import Dict, List, Any

def get_active_alerts(self) -> List[Alert]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Get all active alerts."""
    return list(self.active_alerts.values())
