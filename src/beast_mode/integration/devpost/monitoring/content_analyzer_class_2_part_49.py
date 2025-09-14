from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def get_project_changes_summary(self, since: datetime) -> Dict[str, Any]:
    """Get summary of project changes since a given time."""
    summary = {'total_commits': 0, 'files_changed': 0, 'lines_added': 0, 'lines_removed': 0, 'new_releases': [], 'significant_files': []}
    if not self._git_repo:
        return summary
    try:
        commits = list(self._git_repo.iter_commits(since=since.strftime('%Y-%m-%d %H:%M:%S')))
        summary['total_commits'] = len(commits)
        if commits:
            latest_commit = commits[0]
            if len(commits) > 1:
                diff = latest_commit.diff(commits[-1])
            elif latest_commit.parents:
                diff = latest_commit.diff(latest_commit.parents[0])
            else:
                diff = latest_commit.diff(None)
            summary['files_changed'] = len(diff)
            for item in diff:
                if item.a_blob and item.b_blob:
                    try:
                        summary['lines_added'] += len(item.b_blob.data_stream.read().decode('utf-8', errors='ignore').splitlines())
                        summary['lines_removed'] += len(item.a_blob.data_stream.read().decode('utf-8', errors='ignore').splitlines())
                    except:
                        pass
        summary['new_releases'] = self.detect_git_releases()
        significant_patterns = ['README', 'CHANGELOG', 'package.json', 'pyproject.toml']
        for commit in commits[:5]:
            for item in commit.stats.files:
                file_path = Path(item)
                if any((pattern.lower() in file_path.name.lower() for pattern in significant_patterns)):
                    if str(file_path) not in summary['significant_files']:
                        summary['significant_files'].append(str(file_path))
    except Exception as e:
        logger.error(f'Error getting project changes summary: {e}')
    return summary
