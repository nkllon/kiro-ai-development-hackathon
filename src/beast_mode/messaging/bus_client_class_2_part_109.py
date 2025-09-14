
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
