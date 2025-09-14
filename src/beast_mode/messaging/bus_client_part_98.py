from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def get_message_router_info(self) -> Dict[str, Any]:
    """Get message router information"""
    if self.message_router:
        return self.message_router.get_handler_info()
    return {'error': 'Message router not initialized'}
