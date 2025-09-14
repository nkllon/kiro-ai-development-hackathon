
def validate_metadata(self) -> bool:
    """Validate metadata structure and content"""
    try:
        self._update_metrics('validate_metadata')
        required_fields = ['title', 'description', 'version']
        for field in required_fields:
            if field not in self.metadata or not self.metadata[field]:
                self._logger.warning(f'Missing required metadata field: {field}')
                return False
        return True
    except Exception as e:
        self._logger.error(f'Metadata validation failed: {e}')
        self._metrics['error_count'] += 1
        return False
