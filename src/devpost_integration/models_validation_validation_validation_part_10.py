
def validate_data(self, data: Dict[str, Any], rules: Dict[str, Any]) -> bool:
    """Validate data against rules"""
    try:
        self._update_metrics('validate_data')
        self._metrics['validations_performed'] += 1
        self.clear_errors()
        self.clear_warnings()
        for field, rule in rules.items():
            if field not in data:
                self.add_error(f"Required field '{field}' is missing", field)
            elif rule.get('required') and (not data[field]):
                self.add_error(f"Field '{field}' is required but empty", field)
            elif rule.get('type') and (not isinstance(data[field], rule['type'])):
                self.add_error(f"Field '{field}' must be of type {rule['type'].__name__}", field)
            elif rule.get('min_length') and len(str(data[field])) < rule['min_length']:
                self.add_error(f"Field '{field}' is too short (minimum {rule['min_length']} characters)", field)
            elif rule.get('max_length') and len(str(data[field])) > rule['max_length']:
                self.add_error(f"Field '{field}' is too long (maximum {rule['max_length']} characters)", field)
        self.updated_at = datetime.now()
        self._logger.info(f'Data validation completed: {self.is_valid}')
        return self.is_valid
    except Exception as e:
        self._logger.error(f'Data validation failed: {e}')
        self._metrics['error_count'] += 1
        return False
