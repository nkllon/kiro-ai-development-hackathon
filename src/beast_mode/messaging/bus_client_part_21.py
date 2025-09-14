from datetime import datetime
from typing import Dict, List, Any

    def find_agents_with_capabilities(self, required_capabilities: List[str]) -> List[DiscoveredAgent]:
        """
        Find agents that have any of the required capabilities.
        
        Args:
            required_capabilities: List of required capabilities
            
        Returns:
            List[DiscoveredAgent]: Agents with matching capabilities
        """
        if not self.discovery_enabled:
            return []
        return self.agent_registry.find_agents_with_capabilities(required_capabilities)
