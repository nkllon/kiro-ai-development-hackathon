from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def get_message_history(self, limit: Optional[int]=None) -> Dict[str, List[BeastModeMessage]]:
    """
        Get message history from the router.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            Message history
        """
    if self.message_router:
        return self.message_router.get_message_history(limit)
    recent_messages = self.received_messages[-limit:] if limit else self.received_messages
    return {'sent': [], 'received': recent_messages}
