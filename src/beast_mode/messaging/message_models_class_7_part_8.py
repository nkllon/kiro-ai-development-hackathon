from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def create_help_request(sender_id: str, required_capabilities: List[AgentCapability], description: str, priority: str='normal') -> BeastModeMessage:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Create a help request message."""
    return BeastModeMessage(message_type=MessageType.HELP_REQUEST, sender_id=sender_id, subject='Help Request', content={'description': description, 'required_capabilities': [cap.value for cap in required_capabilities], 'deadline': None}, capabilities_required=required_capabilities, priority=priority, requires_response=True)

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

