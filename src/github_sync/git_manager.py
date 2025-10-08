"""
Git commit management for GitHub synchronization.

This module provides intelligent commit creation and Git best practices
for managing version control in the GitHub synchronization system.
"""

import os
import subprocess
import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import re

logger = logging.getLogger(__name__)


@dataclass
class FileChange:
    """Represents a file change for commit grouping."""
    path: str
    change_type: str  # 'added', 'modified', 'deleted'
    content_type: str  # 'code', 'config', 'docs', 'test', 'data'
    size_bytes: int
    
    
@dataclass
class CommitGroup:
    """Represents a logical group of related changes."""
    files: List[FileChange]
    commit_type: str  # 'feat', 'fix', 'docs', 'refactor', 'test', 'chore'
    scope: Optional[str]  # component or module affected
    description: str
    breaking_change: bool = False


class GitCommitManager:
    """
    Manages intelligent Git commit creation and version control best practices.
    
    This class groups related changes into logical commits with descriptive
    messages following conventional commit standards.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize Git commit manager.
        
        Args:
            repo_path: Path to the Git repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Validate Git repository
        if not self._is_git_repository():
            raise ValueError(f"Path {repo_path} is not a Git repository")
    
    def _is_git_repository(self) -> bool:
        """Check if the path is a Git repository."""
        git_dir = self.repo_path / ".git"
        return git_dir.exists() and (git_dir.is_dir() or git_dir.is_file())
    
    def _run_git_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        Run a Git command in the repository.
        
        Args:
            args: Git command arguments
            check: Whether to raise exception on non-zero exit code
            
        Returns:
            CompletedProcess result
        """
        cmd = ["git"] + args
        self.logger.debug(f"Running Git command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check
            )
            
            if result.stdout:
                self.logger.debug(f"Git stdout: {result.stdout.strip()}")
            if result.stderr:
                self.logger.debug(f"Git stderr: {result.stderr.strip()}")
                
            return result
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git command failed: {' '.join(cmd)}")
            self.logger.error(f"Exit code: {e.returncode}")
            self.logger.error(f"Stdout: {e.stdout}")
            self.logger.error(f"Stderr: {e.stderr}")
            raise
    
    def get_staged_changes(self) -> List[FileChange]:
        """
        Get list of staged file changes.
        
        Returns:
            List of FileChange objects for staged files
        """
        # Get staged files with their status
        result = self._run_git_command(["diff", "--cached", "--name-status"])
        
        changes = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
                
            parts = line.split('\t', 1)
            if len(parts) != 2:
                continue
                
            status, filepath = parts
            change_type = self._map_git_status_to_change_type(status)
            
            # Get file size
            file_path = self.repo_path / filepath
            size_bytes = 0
            if file_path.exists():
                size_bytes = file_path.stat().st_size
            
            # Determine content type
            content_type = self._determine_content_type(filepath)
            
            changes.append(FileChange(
                path=filepath,
                change_type=change_type,
                content_type=content_type,
                size_bytes=size_bytes
            ))
        
        return changes
    
    def _map_git_status_to_change_type(self, status: str) -> str:
        """Map Git status codes to change types."""
        status_map = {
            'A': 'added',
            'M': 'modified',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied',
            'U': 'unmerged'
        }
        return status_map.get(status[0], 'modified')
    
    def _determine_content_type(self, filepath: str) -> str:
        """
        Determine the content type of a file based on its path and extension.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Content type string
        """
        path = Path(filepath)
        
        # Test files
        if 'test' in str(path).lower() or path.suffix in ['.test.py', '.spec.py']:
            return 'test'
        
        # Documentation files
        if path.suffix.lower() in ['.md', '.rst', '.txt', '.adoc']:
            return 'docs'
        
        # Configuration files
        config_patterns = [
            r'.*\.ya?ml$', r'.*\.json$', r'.*\.toml$', r'.*\.ini$',
            r'.*\.cfg$', r'.*\.conf$', r'Dockerfile.*', r'.*\.env.*'
        ]
        if any(re.match(pattern, str(path), re.IGNORECASE) for pattern in config_patterns):
            return 'config'
        
        # Code files
        code_extensions = [
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
            '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt'
        ]
        if path.suffix.lower() in code_extensions:
            return 'code'
        
        # Data files
        data_extensions = ['.csv', '.json', '.xml', '.sql', '.db', '.sqlite']
        if path.suffix.lower() in data_extensions:
            return 'data'
        
        return 'other'
    
    def group_changes_for_commits(self, changes: List[FileChange]) -> List[CommitGroup]:
        """
        Group file changes into logical commits.
        
        Args:
            changes: List of file changes to group
            
        Returns:
            List of commit groups
        """
        if not changes:
            return []
        
        # Group changes by content type and scope
        groups = {}
        
        for change in changes:
            # Determine scope (directory or module)
            scope = self._determine_scope(change.path)
            
            # Create grouping key
            key = (change.content_type, scope)
            
            if key not in groups:
                groups[key] = []
            groups[key].append(change)
        
        # Convert groups to CommitGroup objects
        commit_groups = []
        for (content_type, scope), file_changes in groups.items():
            commit_type = self._determine_commit_type(content_type, file_changes)
            description = self._generate_commit_description(commit_type, scope, file_changes)
            
            commit_groups.append(CommitGroup(
                files=file_changes,
                commit_type=commit_type,
                scope=scope,
                description=description,
                breaking_change=self._has_breaking_changes(file_changes)
            ))
        
        # Sort groups by priority (tests last, critical changes first)
        commit_groups.sort(key=self._commit_group_priority)
        
        return commit_groups
    
    def _determine_scope(self, filepath: str) -> Optional[str]:
        """
        Determine the scope (component/module) for a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Scope string or None
        """
        path = Path(filepath)
        parts = path.parts
        
        # For src/ structure, use the first subdirectory
        if len(parts) > 1 and parts[0] == 'src':
            if len(parts) > 2:
                return parts[1]
            return 'core'
        
        # For other structures, use the first directory
        if len(parts) > 1:
            return parts[0]
        
        return None
    
    def _determine_commit_type(self, content_type: str, changes: List[FileChange]) -> str:
        """
        Determine the conventional commit type based on content and changes.
        
        Args:
            content_type: Type of content being changed
            changes: List of file changes
            
        Returns:
            Commit type string
        """
        # Test files
        if content_type == 'test':
            return 'test'
        
        # Documentation
        if content_type == 'docs':
            return 'docs'
        
        # Configuration changes
        if content_type == 'config':
            return 'chore'
        
        # Code changes - determine if feat or fix
        if content_type == 'code':
            # Check if this looks like a new feature (new files)
            new_files = [c for c in changes if c.change_type == 'added']
            if new_files:
                return 'feat'
            
            # Check for bug fix patterns in file names
            bug_patterns = ['fix', 'bug', 'error', 'issue']
            for change in changes:
                if any(pattern in change.path.lower() for pattern in bug_patterns):
                    return 'fix'
            
            # Default to refactor for code modifications
            return 'refactor'
        
        # Default to chore
        return 'chore'
    
    def _generate_commit_description(self, commit_type: str, scope: Optional[str], 
                                   changes: List[FileChange]) -> str:
        """
        Generate a descriptive commit message.
        
        Args:
            commit_type: Type of commit
            scope: Scope of changes
            changes: List of file changes
            
        Returns:
            Commit description
        """
        # Count changes by type
        added = len([c for c in changes if c.change_type == 'added'])
        modified = len([c for c in changes if c.change_type == 'modified'])
        deleted = len([c for c in changes if c.change_type == 'deleted'])
        
        # Generate description based on commit type
        if commit_type == 'feat':
            if scope:
                return f"add new {scope} functionality"
            return "add new functionality"
        
        elif commit_type == 'fix':
            if scope:
                return f"fix issues in {scope}"
            return "fix issues"
        
        elif commit_type == 'docs':
            if added and not modified and not deleted:
                return "add documentation"
            elif modified and not added and not deleted:
                return "update documentation"
            else:
                return "update documentation"
        
        elif commit_type == 'test':
            if added:
                return "add tests"
            elif modified:
                return "update tests"
            else:
                return "update tests"
        
        elif commit_type == 'refactor':
            if scope:
                return f"refactor {scope} implementation"
            return "refactor implementation"
        
        elif commit_type == 'chore':
            if scope:
                return f"update {scope} configuration"
            return "update configuration"
        
        # Fallback description
        total_files = len(changes)
        if total_files == 1:
            return f"update {changes[0].path}"
        else:
            return f"update {total_files} files"
    
    def _has_breaking_changes(self, changes: List[FileChange]) -> bool:
        """
        Determine if changes include breaking changes.
        
        Args:
            changes: List of file changes
            
        Returns:
            True if breaking changes detected
        """
        # Look for patterns that might indicate breaking changes
        breaking_patterns = [
            'breaking', 'major', 'incompatible', 'migration',
            'deprecated', 'removed', 'deleted'
        ]
        
        for change in changes:
            path_lower = change.path.lower()
            if any(pattern in path_lower for pattern in breaking_patterns):
                return True
        
        return False
    
    def _commit_group_priority(self, group: CommitGroup) -> int:
        """
        Determine priority for commit group ordering.
        
        Args:
            group: Commit group to prioritize
            
        Returns:
            Priority value (lower = higher priority)
        """
        # Priority order: fix, feat, refactor, docs, chore, test
        priority_map = {
            'fix': 1,
            'feat': 2,
            'refactor': 3,
            'docs': 4,
            'chore': 5,
            'test': 6
        }
        
        return priority_map.get(group.commit_type, 10)
    
    def create_commit(self, group: CommitGroup, dry_run: bool = False) -> bool:
        """
        Create a Git commit for a group of changes.
        
        Args:
            group: Commit group to commit
            dry_run: If True, don't actually create the commit
            
        Returns:
            True if commit was successful
        """
        try:
            # Stage the specific files for this commit
            for file_change in group.files:
                if not dry_run:
                    self._run_git_command(["add", file_change.path])
            
            # Generate commit message
            message = self._format_commit_message(group)
            
            if dry_run:
                self.logger.info(f"Would create commit: {message}")
                self.logger.info(f"Files: {[f.path for f in group.files]}")
                return True
            
            # Create the commit
            self._run_git_command(["commit", "-m", message])
            
            self.logger.info(f"Created commit: {message}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create commit: {e}")
            return False
    
    def _format_commit_message(self, group: CommitGroup) -> str:
        """
        Format a conventional commit message.
        
        Args:
            group: Commit group
            
        Returns:
            Formatted commit message
        """
        # Start with type
        message = group.commit_type
        
        # Add scope if present
        if group.scope:
            message += f"({group.scope})"
        
        # Add breaking change indicator
        if group.breaking_change:
            message += "!"
        
        # Add description
        message += f": {group.description}"
        
        # Add body with file details if multiple files
        if len(group.files) > 1:
            message += "\n\n"
            for file_change in group.files:
                action = file_change.change_type.capitalize()
                message += f"- {action} {file_change.path}\n"
        
        return message
    
    def create_intelligent_commits(self, dry_run: bool = False) -> List[str]:
        """
        Create intelligent commits for all staged changes.
        
        Args:
            dry_run: If True, don't actually create commits
            
        Returns:
            List of commit messages created
        """
        # Get staged changes
        changes = self.get_staged_changes()
        
        if not changes:
            self.logger.info("No staged changes found")
            return []
        
        # Group changes into logical commits
        commit_groups = self.group_changes_for_commits(changes)
        
        if not commit_groups:
            self.logger.warning("No commit groups created from changes")
            return []
        
        # Create commits for each group
        commit_messages = []
        for group in commit_groups:
            if self.create_commit(group, dry_run=dry_run):
                message = self._format_commit_message(group)
                commit_messages.append(message)
        
        return commit_messages
    
    def get_repository_status(self) -> Dict[str, any]:
        """
        Get comprehensive repository status.
        
        Returns:
            Dictionary with repository status information
        """
        try:
            # Get current branch
            branch_result = self._run_git_command(["branch", "--show-current"])
            current_branch = branch_result.stdout.strip()
            
            # Get status
            status_result = self._run_git_command(["status", "--porcelain"])
            status_lines = status_result.stdout.strip().split('\n') if status_result.stdout.strip() else []
            
            # Count file states
            staged = len([line for line in status_lines if line and line[0] in 'AMDR'])
            unstaged = len([line for line in status_lines if line and line[1] in 'AMDR'])
            untracked = len([line for line in status_lines if line and line.startswith('??')])
            
            # Get last commit info
            try:
                last_commit_result = self._run_git_command(["log", "-1", "--format=%H|%s|%an|%ad", "--date=iso"])
                if last_commit_result.stdout.strip():
                    commit_parts = last_commit_result.stdout.strip().split('|', 3)
                    last_commit = {
                        'hash': commit_parts[0][:8],
                        'message': commit_parts[1],
                        'author': commit_parts[2],
                        'date': commit_parts[3]
                    }
                else:
                    last_commit = None
            except subprocess.CalledProcessError:
                last_commit = None
            
            return {
                'current_branch': current_branch,
                'staged_files': staged,
                'unstaged_files': unstaged,
                'untracked_files': untracked,
                'last_commit': last_commit,
                'is_clean': staged == 0 and unstaged == 0 and untracked == 0
            }
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get repository status: {e}")
            return {
                'error': str(e),
                'current_branch': 'unknown',
                'staged_files': 0,
                'unstaged_files': 0,
                'untracked_files': 0,
                'last_commit': None,
                'is_clean': False
            }