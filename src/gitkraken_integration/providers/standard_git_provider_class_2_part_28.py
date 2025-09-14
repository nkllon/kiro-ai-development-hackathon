from src.rm_ddd.core.registry import register_module

    def compare_branches(self, branch1: str, branch2: str) -> GitOperationResult:
        """Compare two branches and show differences"""
        start_time = time.time()
        try:
            ahead_result = self._run_git_command(['rev-list', '--count', f'{branch2}..{branch1}'])
            ahead_count = int(ahead_result.stdout.strip())
            behind_result = self._run_git_command(['rev-list', '--count', f'{branch1}..{branch2}'])
            behind_count = int(behind_result.stdout.strip())
            commits_ahead = []
            if ahead_count > 0:
                commits_ahead_result = self._run_git_command(['log', '--format=%H|%s|%an|%ci', f'{branch2}..{branch1}'])
                for line in commits_ahead_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 4:
                            commits_ahead.append({'hash': parts[0], 'message': parts[1], 'author': parts[2], 'date': parts[3]})
            commits_behind = []
            if behind_count > 0:
                commits_behind_result = self._run_git_command(['log', '--format=%H|%s|%an|%ci', f'{branch1}..{branch2}'])
                for line in commits_behind_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 4:
                            commits_behind.append({'hash': parts[0], 'message': parts[1], 'author': parts[2], 'date': parts[3]})
            if ahead_count == 0 and behind_count == 0:
                relationship = 'identical'
            elif ahead_count > 0 and behind_count == 0:
                relationship = f'{branch1} is ahead'
            elif ahead_count == 0 and behind_count > 0:
                relationship = f'{branch1} is behind'
            else:
                relationship = 'diverged'
            execution_time = int((time.time() - start_time) * 1000)
            return self._create_result(success=True, message=f"Compared branches '{branch1}' and '{branch2}': {relationship}", data={'branch1': branch1, 'branch2': branch2, 'relationship': relationship, 'ahead_count': ahead_count, 'behind_count': behind_count, 'commits_ahead': commits_ahead, 'commits_behind': commits_behind, 'can_fast_forward': behind_count == 0 and ahead_count > 0}, execution_time_ms=execution_time)
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            suggestions = []
            if 'unknown revision' in e.stderr:
                suggestions.extend(['One or both branches do not exist', 'Check branch names with list_branches()'])
            return self._create_result(success=False, message=f"Failed to compare branches '{branch1}' and '{branch2}': {e.stderr}", error_code='GIT_COMPARE_BRANCHES_FAILED', suggestions=suggestions, execution_time_ms=execution_time)
