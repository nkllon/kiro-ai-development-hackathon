
def _convert_from_v1_1(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert from V1.1 format"""
    converted = message_data.copy()
    if 'request_id' in converted and 'correlation_id' not in converted:
        converted['correlation_id'] = converted.pop('request_id')
    return converted
