from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _get_commit_details(self, commit_hash: str) -> Tuple[datetime, str]:
    """Get commit date and author for a specific commit"""
    try:
        result = self._run_git_command(['show', '-s', '--format=%ci|%an', commit_hash])
        parts = result.stdout.strip().split('|')
        if len(parts) == 2:
            date_str, author = parts
            commit_date = datetime.fromisoformat(date_str.replace(' ', 'T', 1))
            return (commit_date, author)
    except (subprocess.CalledProcessError, ValueError):
        pass
    return (datetime.now(), 'Unknown')
