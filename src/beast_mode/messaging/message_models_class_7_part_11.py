from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def filter_messages_by_capability(messages: List[BeastModeMessage], agent_capabilities: List[AgentCapability]) -> List[BeastModeMessage]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Filter messages that match agent capabilities."""
    filtered = []
    for msg in messages:
        if not msg.capabilities_required:
            filtered.append(msg)
        elif any((cap in agent_capabilities for cap in msg.capabilities_required)):
            filtered.append(msg)
    return filtered
