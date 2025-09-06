"""
GitAnalyzer - Git analysis component for compliance checking.

This module implements git repository analysis capabilities for the Beast Mode
compliance checking system, including commit analysis and file change detection.
"""

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from ...core.reflective_module import ReflectiveModule
from ..interfaces import ComplianceAnalyzer, ValidationContext
from ..models import (
    ComplianceAnalysisResult,
    CommitInfo,
    FileChangeAnalysis,
    ComplianceIssue,
    ComplianceIssueType,
    IssueSeverity
)


class GitAnalyzer(ReflectiveModule, ComplianceAnalyzer):
    """
    Git analysis component for identifying changes ahead of main.
    
    Analyzes git commits and file changes to support compliance checking
    by identifying the commits ahead of main and analyzing their content.
    """
    
    def __init__(self, repository_path: str = "."):
        """
        Initialize the GitAnalyzer.
        
        Args:
            repository_path: Path to the git repository to analyze
        """
        super().__init__("GitAnalyzer")
        self.repository_path = Path(repository_path).resolve()
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self._config = {
            "target_branch": "main",
            "base_branch": "origin/master",
            "max_commits_to_analyze": 10,
            "git_timeout": 30
        }
        
        self.logger.info(f"GitAnalyzer initialized for repository: {self.repository_path}")
    
    def get_commits_ahead_of_main(self, target_branch: str = "HEAD", base_branch: str = "origin/master") -> List[CommitInfo]:
        """
        Get the commits ahead of the base branch.
        
        Args:
            target_branch: The target branch to compare (default: HEAD)
            base_branch: The base branch to compare against (default: origin/master)
            
        Returns:
            List of CommitInfo objects for commits ahead of base
        """
        self.logger.info(f"Analyzing commits ahead of {base_branch} on {target_branch}")
        
        try:
            # Get commit hashes ahead of base
            commit_hashes = self._get_commit_hashes_ahead(target_branch, base_branch)
            
            if not commit_hashes:
                self.logger.info("No commits found ahead of base branch")
                return []
            
            # Limit the number of commits to analyze
            if len(commit_hashes) > self._config["max_commits_to_analyze"]:
                self.logger.warning(
                    f"Found {len(commit_hashes)} commits, limiting to {self._config['max_commits_to_analyze']}"
                )
                commit_hashes = commit_hashes[:self._config["max_commits_to_analyze"]]
            
            # Get detailed information for each commit
            commits = []
            for commit_hash in commit_hashes:
                commit_info = self._get_commit_info(commit_hash)
                if commit_info:
                    commits.append(commit_info)
            
            self.logger.info(f"Successfully analyzed {len(commits)} commits ahead of {base_branch}")
            return commits
            
        except Exception as e:
            self.logger.error(f"Error getting commits ahead of main: {str(e)}")
            raise
    
    def analyze_file_changes(self, commits: Optional[List[CommitInfo]] = None) -> FileChangeAnalysis:
        """
        Analyze file changes across the provided commits or commits ahead of main.
        
        Args:
            commits: Optional list of commits to analyze. If None, analyzes commits ahead of main.
            
        Returns:
            FileChangeAnalysis with comprehensive file change information
        """
        if commits is None:
            commits = self.get_commits_ahead_of_main()
        
        self.logger.info(f"Analyzing file changes across {len(commits)} commits")
        
        try:
            # Aggregate file changes across all commits
            all_added = set()
            all_modified = set()
            all_deleted = set()
            total_lines_added = 0
            total_lines_deleted = 0
            
            for commit in commits:
                all_added.update(commit.added_files)
                all_modified.update(commit.modified_files)
                all_deleted.update(commit.deleted_files)
                
                # Get line changes for this commit
                lines_added, lines_deleted = self._get_commit_line_changes(commit.commit_hash)
                total_lines_added += lines_added
                total_lines_deleted += lines_deleted
            
            # Remove files that were both added and deleted (net zero change)
            net_added = all_added - all_deleted
            net_deleted = all_deleted - all_added
            
            # Files that were modified but not added/deleted
            net_modified = all_modified - all_added - all_deleted
            
            analysis = FileChangeAnalysis(
                total_files_changed=len(net_added) + len(net_modified) + len(net_deleted),
                files_added=sorted(list(net_added)),
                files_modified=sorted(list(net_modified)),
                files_deleted=sorted(list(net_deleted)),
                lines_added=total_lines_added,
                lines_deleted=total_lines_deleted
            )
            
            self.logger.info(
                f"File change analysis complete: {analysis.total_files_changed} files changed "
                f"({len(analysis.files_added)} added, {len(analysis.files_modified)} modified, "
                f"{len(analysis.files_deleted)} deleted)"
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing file changes: {str(e)}")
            raise
    
    def map_changes_to_tasks(self, file_changes: FileChangeAnalysis, task_patterns: Optional[Dict[str, List[str]]] = None) -> Dict[str, List[str]]:
        """
        Map file changes to potential task completions based on patterns.
        
        Args:
            file_changes: The file change analysis results
            task_patterns: Optional mapping of task patterns to file patterns
            
        Returns:
            Dictionary mapping task identifiers to affected files
        """
        self.logger.info("Mapping file changes to potential task completions")
        
        if task_patterns is None:
            task_patterns = self._get_default_task_patterns()
        
        task_mapping = {}
        all_changed_files = (
            file_changes.files_added + 
            file_changes.files_modified + 
            file_changes.files_deleted
        )
        
        for task_id, patterns in task_patterns.items():
            matching_files = []
            
            for file_path in all_changed_files:
                for pattern in patterns:
                    if self._file_matches_pattern(file_path, pattern):
                        matching_files.append(file_path)
                        break
            
            if matching_files:
                task_mapping[task_id] = sorted(list(set(matching_files)))
        
        self.logger.info(f"Mapped changes to {len(task_mapping)} potential tasks")
        return task_mapping
    
    # ComplianceAnalyzer interface implementation
    def analyze(self, context: Dict[str, Any]) -> ComplianceAnalysisResult:
        """
        Analyze git repository for compliance.
        
        Args:
            context: Analysis context containing repository information
            
        Returns:
            Compliance analysis result with git analysis data
        """
        self.logger.info("Starting git compliance analysis")
        
        result = ComplianceAnalysisResult()
        
        try:
            # Extract configuration from context
            target_branch = context.get("target_branch", self._config["target_branch"])
            base_branch = context.get("base_branch", self._config["base_branch"])
            
            # Get commits ahead of main
            result.commits_analyzed = self.get_commits_ahead_of_main(target_branch, base_branch)
            
            # Analyze file changes
            file_changes = self.analyze_file_changes(result.commits_analyzed)
            
            # Store file change analysis in metadata
            result.recommendations.append(
                f"Analyzed {len(result.commits_analyzed)} commits with "
                f"{file_changes.total_files_changed} file changes"
            )
            
            self.logger.info("Git compliance analysis completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during git analysis: {str(e)}")
            result.critical_issues.append(
                ComplianceIssue(
                    issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                    severity=IssueSeverity.CRITICAL,
                    description=f"Git analysis failed: {str(e)}",
                    blocking_merge=True
                )
            )
        
        return result
    
    def get_analyzer_name(self) -> str:
        """Get the name of this analyzer."""
        return "GitAnalyzer"
    
    # ReflectiveModule interface implementation
    def get_module_status(self) -> Dict[str, Any]:
        """Get the current status of the git analyzer."""
        return {
            "module_name": "GitAnalyzer",
            "repository_path": str(self.repository_path),
            "configuration": self._config,
            "is_healthy": self.is_healthy()
        }
    
    def is_healthy(self) -> bool:
        """Check if the git analyzer is healthy."""
        try:
            return (
                self.repository_path.exists() and
                self.repository_path.is_dir() and
                (self.repository_path / ".git").exists() and
                self._can_execute_git_commands()
            )
        except Exception:
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health metrics for operational visibility."""
        indicators = {}
        
        try:
            # Repository health
            repo_exists = self.repository_path.exists()
            git_exists = (self.repository_path / ".git").exists() if repo_exists else False
            git_executable = self._can_execute_git_commands()
            
            indicators["repository_accessible"] = {
                "status": "healthy" if repo_exists else "unhealthy",
                "value": repo_exists,
                "message": f"Repository at {self.repository_path} {'exists' if repo_exists else 'not found'}"
            }
            
            indicators["git_repository"] = {
                "status": "healthy" if git_exists else "unhealthy",
                "value": git_exists,
                "message": "Git repository detected" if git_exists else "Not a git repository"
            }
            
            indicators["git_executable"] = {
                "status": "healthy" if git_executable else "unhealthy",
                "value": git_executable,
                "message": "Git commands executable" if git_executable else "Cannot execute git commands"
            }
            
        except Exception as e:
            indicators["error"] = {
                "status": "unhealthy",
                "value": str(e),
                "message": f"Error getting health indicators: {str(e)}"
            }
        
        return indicators
    
    def _get_primary_responsibility(self) -> str:
        """Define the single primary responsibility of this module."""
        return "Analyze git repository commits and file changes for compliance checking"
    
    # Private helper methods
    def _get_commit_hashes_ahead(self, target_branch: str, base_branch: str) -> List[str]:
        """Get commit hashes that are ahead of the base branch."""
        try:
            # Use git rev-list to get commits ahead of base
            cmd = [
                "git", "rev-list", 
                f"{base_branch}..{target_branch}",
                "--reverse"  # Get commits in chronological order
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                timeout=self._config["git_timeout"]
            )
            
            if result.returncode != 0:
                self.logger.error(f"Git command failed: {result.stderr}")
                return []
            
            commit_hashes = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            return commit_hashes
            
        except subprocess.TimeoutExpired:
            self.logger.error("Git command timed out")
            return []
        except Exception as e:
            self.logger.error(f"Error getting commit hashes: {str(e)}")
            return []
    
    def _get_commit_info(self, commit_hash: str) -> Optional[CommitInfo]:
        """Get detailed information for a specific commit."""
        try:
            # Get commit metadata
            cmd = [
                "git", "show", 
                "--format=%H|%an|%at|%s",
                "--name-status",
                "--no-merges",
                commit_hash
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                timeout=self._config["git_timeout"]
            )
            
            if result.returncode != 0:
                self.logger.error(f"Failed to get commit info for {commit_hash}: {result.stderr}")
                return None
            
            lines = result.stdout.strip().split('\n')
            if not lines:
                return None
            
            # Parse commit metadata (first line)
            metadata_parts = lines[0].split('|', 3)
            if len(metadata_parts) != 4:
                self.logger.error(f"Invalid commit metadata format for {commit_hash}")
                return None
            
            hash_val, author, timestamp_str, message = metadata_parts
            timestamp = datetime.fromtimestamp(int(timestamp_str))
            
            # Parse file changes
            added_files = []
            modified_files = []
            deleted_files = []
            
            for line in lines[1:]:
                if not line.strip():
                    continue
                
                parts = line.split('\t', 1)
                if len(parts) != 2:
                    continue
                
                status, file_path = parts
                if status == 'A':
                    added_files.append(file_path)
                elif status == 'M':
                    modified_files.append(file_path)
                elif status == 'D':
                    deleted_files.append(file_path)
                elif status.startswith('R'):  # Renamed files
                    # For renames, treat as modified
                    modified_files.append(file_path.split('\t')[-1])
            
            return CommitInfo(
                commit_hash=hash_val,
                author=author,
                timestamp=timestamp,
                message=message,
                modified_files=modified_files,
                added_files=added_files,
                deleted_files=deleted_files
            )
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Git command timed out for commit {commit_hash}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting commit info for {commit_hash}: {str(e)}")
            return None
    
    def _get_commit_line_changes(self, commit_hash: str) -> Tuple[int, int]:
        """Get the number of lines added and deleted in a commit."""
        try:
            cmd = [
                "git", "show", 
                "--numstat",
                "--format=",
                commit_hash
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                timeout=self._config["git_timeout"]
            )
            
            if result.returncode != 0:
                return 0, 0
            
            lines_added = 0
            lines_deleted = 0
            
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 2:
                    try:
                        added = int(parts[0]) if parts[0] != '-' else 0
                        deleted = int(parts[1]) if parts[1] != '-' else 0
                        lines_added += added
                        lines_deleted += deleted
                    except ValueError:
                        continue
            
            return lines_added, lines_deleted
            
        except Exception:
            return 0, 0
    
    def _can_execute_git_commands(self) -> bool:
        """Check if git commands can be executed in the repository."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repository_path,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_default_task_patterns(self) -> Dict[str, List[str]]:
        """Get default patterns for mapping files to tasks."""
        return {
            "compliance_infrastructure": [
                "src/beast_mode/compliance/*",
                "tests/*compliance*"
            ],
            "git_analysis": [
                "src/beast_mode/compliance/git/*",
                "tests/*git*"
            ],
            "rdi_validation": [
                "src/beast_mode/compliance/rdi/*",
                "tests/*rdi*"
            ],
            "rm_validation": [
                "src/beast_mode/compliance/rm/*",
                "tests/*rm*"
            ],
            "reporting": [
                "src/beast_mode/compliance/reporting/*",
                "tests/*report*"
            ],
            "documentation": [
                "docs/*",
                "*.md",
                "README*"
            ],
            "tests": [
                "tests/*",
                "*test*.py"
            ]
        }
    
    def _file_matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if a file path matches a given pattern."""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)