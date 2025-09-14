from src.rm_ddd.core.health import ModuleHealth

def _extract_git_metadata(self) -> Optional[Dict[str, Any]]:
    """Extract metadata from Git configuration."""
    git_dir = self.project_root / '.git'
    if not git_dir.exists():
        return None
    metadata = {}
    try:
        git_config_path = git_dir / 'config'
        if git_config_path.exists():
            config_content = git_config_path.read_text(encoding='utf-8')
            url_match = re.search('url\\s*=\\s*(.+)', config_content)
            if url_match:
                url = url_match.group(1).strip()
                if url.startswith('git@'):
                    url = url.replace('git@github.com:', 'https://github.com/')
                    url = url.replace('.git', '')
                metadata['repository_url'] = url
        metadata['contributors'] = []
    except Exception:
        pass
    return metadata if metadata else None
