from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def get_health_status(self) -> Dict[str, Any]:
    """Get client health and statistics"""
    return {'agent_id': self.agent_id, 'is_connected': self.is_connected, 'is_listening': self.is_listening, 'channel': self.channel, 'capabilities': self.capabilities, 'stats': self.stats.copy(), 'message_handlers': list(self.message_handlers.keys())}
