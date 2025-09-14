from src.rm_ddd.core.health import ModuleHealth

class ConverttocurrentClass:
    """Auto-generated class for functions."""

    def convert_to_current(self, message_data: Union[Dict[str, Any], str]) -> ConversionResult:
    """
    Convert message to current format (V2.0).

    Args:
    message_data: Raw message data (dict or JSON string)

    Returns:
    ConversionResult: Conversion result with message or errors
    """
    result = ConversionResult(success=False, target_version=MessageVersion.V2_0)
    try:
    if isinstance(message_data, str):
    try:
    message_data = json.loads(message_data)
    except json.JSONDecodeError as e:
    result.errors.append(f'Invalid JSON: {e}')
    return result
    if not isinstance(message_data, dict):
    result.errors.append('Message data must be a dictionary')
    return result
    source_version = self.detector.detect_version(message_data)
    result.original_version = source_version
    if source_version == MessageVersion.UNKNOWN:
    result.warnings.append('Unknown message format, attempting best-effort conversion')
    converted_data = self._convert_from_version(message_data, source_version)
    try:
    message = BeastModeMessage(**converted_data)
    result.success = True
    result.message = message
    if source_version != MessageVersion.V2_0:
    result.warnings.append(f'Converted from {source_version.value} to {MessageVersion.V2_0.value}')
    except ValidationError as e:
    result.errors.append(f'Validation failed: {e}')
    try:
    lenient_data = self._apply_lenient_conversion(converted_data)
    message = BeastModeMessage(**lenient_data)
    result.success = True
    result.message = message
    result.warnings.append('Applied lenient conversion due to validation errors')
    except ValidationError as e2:
    result.errors.append(f'Lenient conversion also failed: {e2}')
    except Exception as e:
    result.errors.append(f'Conversion error: {e}')
    logger.error(f'Message conversion error: {e}')
    return result

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

