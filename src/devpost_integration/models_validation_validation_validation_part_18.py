from src.rm_ddd.core.health import ModuleHealth

def validate_project(self) -> bool:
    """Validate project data"""
    try:
        self._update_metrics('validate_project')
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in self.project_data or not self.project_data[field]:
                self._logger.warning(f'Missing required field: {field}')
                return False
        return True
    except Exception as e:
        self._logger.error(f'Project validation failed: {e}')
        self._metrics['error_count'] += 1
        return False
