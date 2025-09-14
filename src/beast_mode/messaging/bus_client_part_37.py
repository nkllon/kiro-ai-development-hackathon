from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_message_router_stats(self) -> Dict[str, Any]:
        """Get message router statistics"""
        if self.message_router:
            return self.message_router.get_handler_stats()
        return {'error': 'Message router not initialized'}
