from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def create_test_message(self, msg_type: MessageType, **kwargs) -> BeastModeMessage:
        """
        Create a test message for a specific type.
        
        Args:
            msg_type: Message type to create
            **kwargs: Additional message parameters
            
        Returns:
            Test message
        """
        if self.message_router:
            return self.message_router.create_test_message(msg_type, **kwargs)
        return BeastModeMessage(type=msg_type, source=kwargs.get('source', self.agent_id), target=kwargs.get('target'), payload=kwargs.get('payload', {}), priority=kwargs.get('priority', 5))

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

