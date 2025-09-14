
def cleanup_inactive_agents(self) -> int:
    """
        Manually trigger cleanup of inactive agents.
        
        Returns:
            int: Number of agents cleaned up
        """
    if not self.discovery_enabled:
        return 0
    return self.agent_registry.cleanup_inactive_agents()
