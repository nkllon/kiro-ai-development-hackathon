from src.rm_ddd.core.health import ModuleHealth

def process_message(self, message_data: Union[Dict[str, Any], str, BeastModeMessage]) -> ConversionResult:
    """
        Process incoming message with compatibility handling.
        
        Args:
            message_data: Raw message data in any supported format
            
        Returns:
            ConversionResult: Processing result
        """
    self.stats['messages_processed'] += 1
    self.stats['last_activity'] = datetime.now()
    if isinstance(message_data, BeastModeMessage):
        result = ConversionResult(success=True, message=message_data)
        result.original_version = MessageVersion.V2_0
        result.target_version = MessageVersion.V2_0
        return result
    result = self.converter.convert_to_current(message_data)
    if self.strict_validation and (not result.success or result.original_version == MessageVersion.UNKNOWN):
        result.success = False
        if not result.errors:
            result.errors.append('Message format not supported in strict mode')
        self.stats['conversions_failed'] += 1
        return result
    if result.success:
        self.stats['conversions_successful'] += 1
        if result.original_version:
            version_key = result.original_version.value
            self.stats['version_distribution'][version_key] = self.stats['version_distribution'].get(version_key, 0) + 1
    else:
        self.stats['conversions_failed'] += 1
    if result.message:
        original_type_str = str(message_data.get('type', '')) if isinstance(message_data, dict) else ''
        if original_type_str and original_type_str in self.unknown_type_handlers:
            result.message.type = self.unknown_type_handlers[original_type_str]
            result.warnings.append(f'Mapped unknown type to {result.message.type.value}')
            self.stats['unknown_types_handled'] += 1
        elif self._is_unknown_type(result.message.type):
            handled_type = self._handle_unknown_type(result.message.type)
            if handled_type and handled_type != result.message.type:
                result.message.type = handled_type
                result.warnings.append(f'Mapped unknown type to {handled_type.value}')
                self.stats['unknown_types_handled'] += 1
    return result
