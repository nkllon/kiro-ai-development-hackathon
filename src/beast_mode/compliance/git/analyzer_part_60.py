from src.rm_ddd.core.health import ModuleHealth

def get_module_status(self) -> Dict[str, Any]:
    """Get the current status of the git analyzer."""
    return {'module_name': 'GitAnalyzer', 'repository_path': str(self.repository_path), 'configuration': self._config, 'is_healthy': self.is_healthy()}
