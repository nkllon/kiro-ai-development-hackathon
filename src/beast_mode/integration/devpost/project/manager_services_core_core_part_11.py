from src.rm_ddd.core.health import ModuleHealth

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
