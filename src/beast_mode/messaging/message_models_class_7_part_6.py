from src.rm_ddd.core.registry import register_module

def create_agent_announcement(agent_id: str, capabilities: AgentCapabilities) -> BeastModeMessage:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Create an agent announcement message."""
    if hasattr(capabilities, 'model_dump'):
        caps_dict = capabilities.model_dump()
    elif hasattr(capabilities, 'to_dict'):
        caps_dict = capabilities.to_dict()
    else:
        caps_dict = capabilities.__dict__.copy()
