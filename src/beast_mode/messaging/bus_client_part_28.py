from datetime import datetime
from typing import Dict, List, Any

    def get_discovery_stats(self) -> Dict:
        """Get agent discovery statistics"""
        if not self.discovery_enabled:
            return {'discovery_enabled': False}
        return {'discovery_enabled': True, **self.agent_registry.get_registry_stats()}
