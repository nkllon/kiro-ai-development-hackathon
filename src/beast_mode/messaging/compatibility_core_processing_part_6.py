from src.rm_ddd.core.health import ModuleHealth

class ConverttolegacyClass:
    """Auto-generated class for functions."""

    def convert_to_legacy(self, message: BeastModeMessage, target_version: MessageVersion=MessageVersion.V1_0) -> Dict[str, Any]:
    """
    Convert current message to legacy format.

    Args:
    message: Current format message
    target_version: Target legacy version

    Returns:
    Dict[str, Any]: Legacy format message data
    """
    legacy_data = message.model_dump()
    legacy_data['type'] = self.translator.translate_to_legacy(message.type, target_version)
    if target_version == MessageVersion.V1_0:
    legacy_data.pop('correlation_id', None)
    legacy_data.pop('priority', None)
    legacy_data.pop('id', None)
    if 'target' in legacy_data:
    legacy_data['to'] = legacy_data.pop('target')
    if 'source' in legacy_data:
    legacy_data['from'] = legacy_data.pop('source')
    elif target_version == MessageVersion.V1_1:
    legacy_data.pop('id', None)
    if 'correlation_id' in legacy_data:
    legacy_data['request_id'] = legacy_data.pop('correlation_id')
    if 'timestamp' in legacy_data and isinstance(legacy_data['timestamp'], datetime):
    legacy_data['timestamp'] = legacy_data['timestamp'].isoformat()
    return legacy_data

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

