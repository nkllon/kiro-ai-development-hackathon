from datetime import datetime
from typing import Dict, List, Any

def _get_ahead_behind_counts(self, branch: str) -> Dict[str, int]:
    """Get ahead/behind counts for current branch"""
    try:
        result = self._run_git_command(['rev-list', '--left-right', '--count', f'{branch}...@{{u}}'])
        counts = result.stdout.strip().split('\t')
        if len(counts) == 2:
            return {'ahead': int(counts[0]), 'behind': int(counts[1])}
    except subprocess.CalledProcessError:
        pass
    return {'ahead': 0, 'behind': 0}
