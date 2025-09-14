from datetime import datetime
from typing import Dict, List, Any

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
