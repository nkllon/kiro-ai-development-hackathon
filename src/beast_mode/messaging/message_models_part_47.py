from datetime import datetime
from typing import Dict, List, Any

def create_help_request(sender_id: str, required_capabilities: List[AgentCapability], description: str, priority: str='normal') -> BeastModeMessage:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Create a help request message."""
    return BeastModeMessage(message_type=MessageType.HELP_REQUEST, sender_id=sender_id, subject='Help Request', content={'description': description, 'required_capabilities': [cap.value for cap in required_capabilities], 'deadline': None}, capabilities_required=required_capabilities, priority=priority, requires_response=True)
