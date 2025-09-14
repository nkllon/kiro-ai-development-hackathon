
def convert_message(message_data: Union[Dict[str, Any], str]) -> Optional[BeastModeMessage]:
    """
    Convert message data to BeastModeMessage with compatibility handling.
    
    Args:
        message_data: Raw message data
        
    Returns:
        BeastModeMessage or None if conversion fails
    """
    compatibility_layer = MessageCompatibilityLayer(CompatibilityMode.CONVERT)
    result = compatibility_layer.process_message(message_data)
    if result.success:
        return result.message
    else:
        logger.error(f'Message conversion failed: {result.errors}')
        return None
