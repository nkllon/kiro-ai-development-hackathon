from src.rm_ddd.core.health import ModuleHealth

def get_message_history(self, limit: Optional[int]=None) -> Dict[str, List[BeastModeMessage]]:
    """
        Get message history from the router.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            Message history
        """
    if self.message_router:
        return self.message_router.get_message_history(limit)
    recent_messages = self.received_messages[-limit:] if limit else self.received_messages
    return {'sent': [], 'received': recent_messages}

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

