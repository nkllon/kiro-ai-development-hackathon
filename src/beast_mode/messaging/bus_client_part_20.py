from datetime import datetime
from typing import Dict, List, Any

    def get_recent_messages(self, limit: int=10) -> List[BeastModeMessage]:
        """Get recent received messages"""
        return self.received_messages[-limit:] if self.received_messages else []

    async def discover_agents(self) -> List[DiscoveredAgent]:
        """
        Perform agent discovery and return currently known agents.
        
        Returns:
            List[DiscoveredAgent]: List of discovered agents
        """
        if not self.discovery_enabled:
            return []
        await self.announce_presence()
        await asyncio.sleep(1.0)
        return self.agent_registry.get_active_agents()
