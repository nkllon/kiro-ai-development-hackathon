from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _get_git_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Get Git information for a file."""
        if not self._git_repo:
            return None
        try:
            repo_root = Path(self._git_repo.working_dir)
            relative_path = safe_relative_to(file_path, repo_root)
            if relative_path is None:
                return None
            git_info = {}
            try:
                commits = list(self._git_repo.iter_commits(paths=str(relative_path), max_count=1))
                if commits:
                    last_commit = commits[0]
                    git_info.update({'last_commit_hash': last_commit.hexsha, 'last_commit_message': last_commit.message.strip(), 'last_commit_author': str(last_commit.author), 'last_commit_date': last_commit.committed_datetime})
            except Exception:
                pass
            try:
                git_info['is_tracked'] = str(relative_path) in [item.a_path for item in self._git_repo.index.diff(None)]
            except Exception:
                git_info['is_tracked'] = False
            try:
                git_info['is_staged'] = str(relative_path) in [item.a_path for item in self._git_repo.index.diff('HEAD')]
            except Exception:
                git_info['is_staged'] = False
            return git_info if git_info else None
        except Exception as e:
            logger.error(f'Error getting Git info for {file_path}: {e}')
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

