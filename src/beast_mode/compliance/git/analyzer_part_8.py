from src.rm_ddd.core.health import ModuleHealth

    def analyze_file_changes(self, commits: Optional[List[CommitInfo]]=None) -> FileChangeAnalysis:
        """
        Analyze file changes across the provided commits or commits ahead of main.
        
        Args:
            commits: Optional list of commits to analyze. If None, analyzes commits ahead of main.
            
        Returns:
            FileChangeAnalysis with comprehensive file change information
        """
        if commits is None:
            commits = self.get_commits_ahead_of_main()
        self.logger.info(f'Analyzing file changes across {len(commits)} commits')
        try:
            all_added = set()
            all_modified = set()
            all_deleted = set()
            total_lines_added = 0
            total_lines_deleted = 0
            for commit in commits:
                all_added.update(commit.added_files)
                all_modified.update(commit.modified_files)
                all_deleted.update(commit.deleted_files)
                lines_added, lines_deleted = self._get_commit_line_changes(commit.commit_hash)
                total_lines_added += lines_added
                total_lines_deleted += lines_deleted
            net_added = all_added - all_deleted
            net_deleted = all_deleted - all_added
            net_modified = all_modified - all_added - all_deleted
            analysis = FileChangeAnalysis(total_files_changed=len(net_added) + len(net_modified) + len(net_deleted), files_added=sorted(list(net_added)), files_modified=sorted(list(net_modified)), files_deleted=sorted(list(net_deleted)), lines_added=total_lines_added, lines_deleted=total_lines_deleted)
            self.logger.info(f'File change analysis complete: {analysis.total_files_changed} files changed ({len(analysis.files_added)} added, {len(analysis.files_modified)} modified, {len(analysis.files_deleted)} deleted)')
            return analysis
        except Exception as e:
            self.logger.error(f'Error analyzing file changes: {str(e)}')
            raise
