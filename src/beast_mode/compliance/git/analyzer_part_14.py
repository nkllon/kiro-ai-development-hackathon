from src.rm_ddd.core.health import ModuleHealth

class GethealthindicatorsClass:
    """Auto-generated class for functions."""

    def get_health_indicators(self) -> Dict[str, Any]:
    """Get detailed health metrics for operational visibility."""
    indicators = {}
    try:
    repo_exists = self.repository_path.exists()
    git_exists = (self.repository_path / '.git').exists() if repo_exists else False
    git_executable = self._can_execute_git_commands()
    indicators['repository_accessible'] = {'status': 'healthy' if repo_exists else 'unhealthy', 'value': repo_exists, 'message': f"Repository at {self.repository_path} {('exists' if repo_exists else 'not found')}"}
    indicators['git_repository'] = {'status': 'healthy' if git_exists else 'unhealthy', 'value': git_exists, 'message': 'Git repository detected' if git_exists else 'Not a git repository'}
    indicators['git_executable'] = {'status': 'healthy' if git_executable else 'unhealthy', 'value': git_executable, 'message': 'Git commands executable' if git_executable else 'Cannot execute git commands'}
    except Exception as e:
    indicators['error'] = {'status': 'unhealthy', 'value': str(e), 'message': f'Error getting health indicators: {str(e)}'}
    return indicators

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

