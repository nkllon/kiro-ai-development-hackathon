from src.rm_ddd.core.health import ModuleHealth

class ExtractrepositoryurlClass:
    """Auto-generated class for functions."""

    def _extract_repository_url(self, package_data: Dict[str, Any]) -> Optional[str]:
    """Extract repository URL from package data."""
    repo_fields = ['repository', 'homepage', 'url']
    for field in repo_fields:
    if field in package_data:
    repo_info = package_data[field]
    if isinstance(repo_info, str):
    return repo_info
    elif isinstance(repo_info, dict):
    return repo_info.get('url')
    return None

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

