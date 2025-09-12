"""
Git Provider Abstract Interface

This module defines the abstract interface for git operations that all providers
must implement. It follows the progressive enhancement principle where standard
git is the baseline and GitKraken API provides enhanced features.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class GitOperationStatus(Enum):
    """Status of git operations"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    CONFLICT = "conflict"
    TIMEOUT = "timeout"


@dataclass
class GitOperationResult:
    """Result of a git operation with comprehensive metadata"""
    success: bool
    status: GitOperationStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    provider_used: str = ""
    execution_time_ms: int = 0
    error_code: Optional[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        
        # Ensure status matches success flag
        if self.success and self.status == GitOperationStatus.FAILURE:
            self.status = GitOperationStatus.SUCCESS
        elif not self.success and self.status == GitOperationStatus.SUCCESS:
            self.status = GitOperationStatus.FAILURE


@dataclass
class BranchInfo:
    """Comprehensive branch information"""
    name: str
    is_current: bool
    ahead_count: int
    behind_count: int
    last_commit_hash: str
    last_commit_message: str
    last_commit_date: datetime
    last_commit_author: str
    tracking_branch: Optional[str] = None
    is_dirty: bool = False
    untracked_files: int = 0
    modified_files: int = 0
    staged_files: int = 0


@dataclass
class CommitInfo:
    """Detailed commit information"""
    hash: str
    short_hash: str
    message: str
    author_name: str
    author_email: str
    committer_name: str
    committer_email: str
    commit_date: datetime
    author_date: datetime
    parent_hashes: List[str]
    changed_files: List[str]
    insertions: int
    deletions: int


@dataclass
class FileStatus:
    """Status of a file in the working directory"""
    path: str
    status: str  # 'M', 'A', 'D', 'R', 'C', 'U', '??', etc.
    staged: bool
    working_tree_status: str
    index_status: str


@dataclass
class MergeConflict:
    """Information about merge conflicts"""
    file_path: str
    conflict_type: str  # 'content', 'rename', 'delete', etc.
    our_version: Optional[str] = None
    their_version: Optional[str] = None
    base_version: Optional[str] = None
    resolution_suggestions: List[str] = None
    
    def __post_init__(self):
        if self.resolution_suggestions is None:
            self.resolution_suggestions = []


class GitProvider(ABC):
    """
    Abstract interface for git operations.
    
    This interface defines all git operations that providers must implement.
    It follows the progressive enhancement principle where standard git
    provides baseline functionality and GitKraken API provides enhancements.
    """
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    # Core Status and Information Methods
    
    @abstractmethod
    def get_status(self) -> GitOperationResult:
        """
        Get comprehensive repository status.
        
        Returns:
            GitOperationResult with status data including:
            - clean: bool - whether working tree is clean
            - files: List[FileStatus] - status of all files
            - branch: str - current branch name
            - ahead_behind: Dict[str, int] - ahead/behind counts
        """
        pass
    
    @abstractmethod
    def get_current_branch(self) -> GitOperationResult:
        """
        Get current branch information.
        
        Returns:
            GitOperationResult with current branch name and metadata
        """
        pass
    
    @abstractmethod
    def list_branches(self, include_remote: bool = True) -> GitOperationResult:
        """
        List all branches with comprehensive metadata.
        
        Args:
            include_remote: Whether to include remote branches
            
        Returns:
            GitOperationResult with List[BranchInfo] in data
        """
        pass
    
    # Branch Management Methods
    
    @abstractmethod
    def create_branch(self, name: str, from_branch: str = "HEAD") -> GitOperationResult:
        """
        Create a new branch.
        
        Args:
            name: Name of the new branch
            from_branch: Branch or commit to create from
            
        Returns:
            GitOperationResult with branch creation status
        """
        pass
    
    @abstractmethod
    def switch_branch(self, name: str, create_if_missing: bool = False) -> GitOperationResult:
        """
        Switch to a branch.
        
        Args:
            name: Branch name to switch to
            create_if_missing: Create branch if it doesn't exist
            
        Returns:
            GitOperationResult with switch status
        """
        pass
    
    @abstractmethod
    def delete_branch(self, name: str, force: bool = False) -> GitOperationResult:
        """
        Delete a branch.
        
        Args:
            name: Branch name to delete
            force: Force delete even if not merged
            
        Returns:
            GitOperationResult with deletion status
        """
        pass
    
    @abstractmethod
    def merge_branch(self, source: str, target: str = None) -> GitOperationResult:
        """
        Merge branches.
        
        Args:
            source: Source branch to merge from
            target: Target branch to merge into (current if None)
            
        Returns:
            GitOperationResult with merge status and conflict info
        """
        pass
    
    # Commit and Change Management Methods
    
    @abstractmethod
    def stage_files(self, files: List[str] = None) -> GitOperationResult:
        """
        Stage files for commit.
        
        Args:
            files: List of files to stage (all if None)
            
        Returns:
            GitOperationResult with staging status
        """
        pass
    
    @abstractmethod
    def unstage_files(self, files: List[str] = None) -> GitOperationResult:
        """
        Unstage files.
        
        Args:
            files: List of files to unstage (all if None)
            
        Returns:
            GitOperationResult with unstaging status
        """
        pass
    
    @abstractmethod
    def commit_changes(self, message: str, files: List[str] = None) -> GitOperationResult:
        """
        Commit staged changes.
        
        Args:
            message: Commit message
            files: Specific files to commit (all staged if None)
            
        Returns:
            GitOperationResult with commit hash and metadata
        """
        pass
    
    @abstractmethod
    def get_commit_history(self, branch: str = None, limit: int = 50) -> GitOperationResult:
        """
        Get commit history.
        
        Args:
            branch: Branch to get history for (current if None)
            limit: Maximum number of commits to return
            
        Returns:
            GitOperationResult with List[CommitInfo] in data
        """
        pass
    
    # Remote Operations Methods
    
    @abstractmethod
    def push_changes(self, branch: str = None, remote: str = "origin") -> GitOperationResult:
        """
        Push changes to remote.
        
        Args:
            branch: Branch to push (current if None)
            remote: Remote name to push to
            
        Returns:
            GitOperationResult with push status
        """
        pass
    
    @abstractmethod
    def pull_changes(self, branch: str = None, remote: str = "origin") -> GitOperationResult:
        """
        Pull changes from remote.
        
        Args:
            branch: Branch to pull (current if None)
            remote: Remote name to pull from
            
        Returns:
            GitOperationResult with pull status and merge info
        """
        pass
    
    @abstractmethod
    def fetch_changes(self, remote: str = "origin") -> GitOperationResult:
        """
        Fetch changes from remote without merging.
        
        Args:
            remote: Remote name to fetch from
            
        Returns:
            GitOperationResult with fetch status
        """
        pass
    
    # Conflict Resolution Methods
    
    @abstractmethod
    def get_merge_conflicts(self) -> GitOperationResult:
        """
        Get information about current merge conflicts.
        
        Returns:
            GitOperationResult with List[MergeConflict] in data
        """
        pass
    
    @abstractmethod
    def resolve_conflict(self, file_path: str, resolution: str) -> GitOperationResult:
        """
        Resolve a merge conflict.
        
        Args:
            file_path: Path to conflicted file
            resolution: Resolution strategy ('ours', 'theirs', 'manual')
            
        Returns:
            GitOperationResult with resolution status
        """
        pass
    
    # Provider Capability Methods
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this provider is available and functional.
        
        Returns:
            True if provider can be used, False otherwise
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get human-readable provider name.
        
        Returns:
            Provider name for logging and display
        """
        pass
    
    @abstractmethod
    def get_provider_capabilities(self) -> Dict[str, bool]:
        """
        Get provider-specific capabilities.
        
        Returns:
            Dictionary of capability names and availability
        """
        pass
    
    @abstractmethod
    def get_health_status(self) -> GitOperationResult:
        """
        Get provider health status for monitoring.
        
        Returns:
            GitOperationResult with health information
        """
        pass
    
    # Utility Methods
    
    def validate_branch_name(self, name: str) -> bool:
        """
        Validate branch name according to git rules.
        
        Args:
            name: Branch name to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not name or len(name) == 0:
            return False
        
        # Check for whitespace characters (space, tab, newline)
        if any(c.isspace() for c in name):
            return False
        
        # Basic git branch name validation - invalid characters
        invalid_chars = ['~', '^', ':', '?', '*', '[', '\\']
        if any(char in name for char in invalid_chars):
            return False
        
        # Check for double dots
        if '..' in name:
            return False
        
        # Check for double slashes
        if '//' in name:
            return False
        
        # Cannot start or end with certain characters
        if name.startswith('.') or name.endswith('.'):
            return False
        
        if name.startswith('-') or name.endswith('/'):
            return False
        
        # Cannot be empty after stripping
        if name.strip() == '':
            return False
        
        return True
    
    def format_commit_message(self, message: str) -> str:
        """
        Format commit message according to best practices.
        
        Args:
            message: Raw commit message
            
        Returns:
            Formatted commit message
        """
        # Basic formatting - can be enhanced by providers
        lines = message.strip().split('\n')
        if not lines:
            return ""
        
        # Ensure first line is not too long
        first_line = lines[0][:72] if len(lines[0]) > 72 else lines[0]
        
        if len(lines) == 1:
            return first_line
        
        # Add blank line after first line if not present
        formatted_lines = [first_line]
        if len(lines) > 1 and lines[1].strip():
            formatted_lines.append("")
        
        formatted_lines.extend(lines[1:])
        return '\n'.join(formatted_lines)