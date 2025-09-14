from src.rm_ddd.core.health import ModuleHealth

def validate_submission(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate submission against requirements"""
    try:
        self._update_metrics('validate_submission')
        self._metrics['validations_performed'] += 1
        validation_result = {'is_valid': True, 'errors': [], 'warnings': [], 'requirement_id': self.requirement_id}
        if self.requirement_data.get('is_required', True) and (not submission_data.get('files')):
            validation_result['is_valid'] = False
            validation_result['errors'].append('Submission is required but no files provided')
        files = submission_data.get('files', [])
        min_files = self.requirement_data.get('min_files', 1)
        max_files = self.requirement_data.get('max_files', 1)
        if len(files) < min_files:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f'Minimum {min_files} files required, got {len(files)}')
        if len(files) > max_files:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f'Maximum {max_files} files allowed, got {len(files)}')
        allowed_formats = self.requirement_data.get('file_formats', [])
        if allowed_formats:
            for file_info in files:
                file_format = file_info.get('format', '').lower()
                if file_format not in [fmt.lower() for fmt in allowed_formats]:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f'File format {file_format} not allowed')
        max_size = self.requirement_data.get('max_file_size', 10485760)
        min_size = self.requirement_data.get('min_file_size', 0)
        for file_info in files:
            file_size = file_info.get('size', 0)
            if file_size > max_size:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f'File size {file_size} exceeds maximum {max_size}')
            if file_size < min_size:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f'File size {file_size} below minimum {min_size}')
        self._logger.info(f"Submission validation completed for requirement {self.requirement_id}: {validation_result['is_valid']}")
        return validation_result
    except Exception as e:
        self._logger.error(f'Submission validation failed: {e}')
        self._metrics['error_count'] += 1
        return {'is_valid': False, 'errors': [f'Validation error: {str(e)}'], 'warnings': [], 'requirement_id': self.requirement_id}

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

