from datetime import datetime
from typing import Dict, List, Any

def get_discovered_agent(self, agent_id: str) -> Optional[DiscoveredAgent]:
    """Get a specific discovered agent by ID"""
    if not self.discovery_enabled:
        return None
    return self.agent_registry.get_agent(agent_id)
