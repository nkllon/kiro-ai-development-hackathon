
def _convert_from_version(self, message_data: Dict[str, Any], source_version: MessageVersion) -> Dict[str, Any]:
    """Convert message from specific version to current format"""
    converted = message_data.copy()
    if source_version == MessageVersion.V1_0:
        converted = self._convert_from_v1_0(converted)
    elif source_version == MessageVersion.V1_1:
        converted = self._convert_from_v1_1(converted)
    elif source_version == MessageVersion.V1_2:
        converted = self._convert_from_v1_2(converted)
    elif source_version == MessageVersion.UNKNOWN:
        if 'from' in converted or 'content' in converted:
            converted = self._convert_from_v1_0(converted)
    if 'id' not in converted:
        import uuid
        converted['id'] = str(uuid.uuid4())
    if 'timestamp' not in converted:
        converted['timestamp'] = datetime.now()
    elif isinstance(converted['timestamp'], str):
        try:
            converted['timestamp'] = datetime.fromisoformat(converted['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            converted['timestamp'] = datetime.now()
    if 'priority' not in converted:
        converted['priority'] = 5
    if 'payload' not in converted:
        converted['payload'] = {}
    if 'type' in converted:
        try:
            MessageType(converted['type'])
        except ValueError:
            converted['type'] = self.translator.translate_to_current(converted['type']).value
    else:
        converted['type'] = MessageType.SIMPLE_MESSAGE.value
    if 'source' not in converted:
        converted['source'] = 'unknown_agent'
    return converted
