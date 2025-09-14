
def get_commits_ahead_of_main(self, target_branch: str='HEAD', base_branch: str='origin/master') -> List[CommitInfo]:
    """
        Get the commits ahead of the base branch.
        
        Args:
            target_branch: The target branch to compare (default: HEAD)
            base_branch: The base branch to compare against (default: origin/master)
            
        Returns:
            List of CommitInfo objects for commits ahead of base
        """
    self.logger.info(f'Analyzing commits ahead of {base_branch} on {target_branch}')
    try:
        commit_hashes = self._get_commit_hashes_ahead(target_branch, base_branch)
        if not commit_hashes:
            self.logger.info('No commits found ahead of base branch')
            return []
        if len(commit_hashes) > self._config['max_commits_to_analyze']:
            self.logger.warning(f"Found {len(commit_hashes)} commits, limiting to {self._config['max_commits_to_analyze']}")
            commit_hashes = commit_hashes[:self._config['max_commits_to_analyze']]
        commits = []
        for commit_hash in commit_hashes:
            commit_info = self._get_commit_info(commit_hash)
            if commit_info:
                commits.append(commit_info)
        self.logger.info(f'Successfully analyzed {len(commits)} commits ahead of {base_branch}')
        return commits
    except Exception as e:
        self.logger.error(f'Error getting commits ahead of main: {str(e)}')
        raise
