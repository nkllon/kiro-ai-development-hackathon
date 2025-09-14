from datetime import datetime
from typing import Dict, List, Any

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
