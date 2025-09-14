from src.rm_ddd.core.health import ModuleHealth

class ConvertmessageClass:
    """Auto-generated class for functions."""

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

