from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def find_agents_for_capabilities(self, required_capabilities: List[str]) -> List[Dict]:
    """
        Find agents that match the required capabilities.
        
        Args:
            required_capabilities: List of required capabilities
            
        Returns:
            List of agent match information
        """
    matches = self.help_system.find_matching_agents(required_capabilities)
    return [{'agent_id': agent.agent_id, 'capabilities': agent.capabilities.capabilities, 'match_score': score, 'collaboration_score': agent.collaboration_score, 'availability': agent.capabilities.availability, 'last_seen': agent.last_seen.isoformat()} for agent, score in matches]

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

