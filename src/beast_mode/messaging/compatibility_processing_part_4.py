
def _convert_from_v1_0(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert from V1.0 format"""
    converted = message_data.copy()
    if 'from' in converted:
        converted['source'] = converted.pop('from')
    if 'to' in converted:
        converted['target'] = converted.pop('to')
    if 'payload' not in converted:
        standard_fields = {'type', 'source', 'target', 'timestamp', 'priority', 'id', 'correlation_id'}
        payload_data = {}
        fields_to_move = []
        for key, value in converted.items():
            if key not in standard_fields:
                payload_data[key] = value
                fields_to_move.append(key)
        for key in fields_to_move:
            converted.pop(key)
        converted['payload'] = payload_data
    return converted
