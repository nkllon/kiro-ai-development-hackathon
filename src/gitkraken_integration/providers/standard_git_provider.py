"""
Standard Git Provider Implementation

This module provides the baseline git functionality using command-line git operations.
It serves as the foundation that works for all developers without requiring any
premium licenses or additional tools.
"""

import subprocess
import json
import re
import os
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from .git_provider import (
    GitProvider,
    GitOperationResult,
    GitOperationStatus,
    BranchInfo,
    CommitInfo,
    FileStatus,
    MergeConflict
)


class StandardGitProvider(GitProvider):
    """
    Standard git implementation using command-line git operations.
    
    This provider implements all git operations using subprocess calls to the
    git command-line tool. It provides comprehensive functionality that works
    on any system with git installed.
    """
    
    def __init__(self, repo_path: str = "."):
        super().__init__(repo_path)
        self.git_executable = self._find_git_executable()
        self._validate_repository()
    
    def _find_git_executable(self) -> str:
        """Find the git executable on the system"""
        try:
            result = subprocess.run(
                ["which", "git"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            # Try common locations
            common_paths = ["/usr/bin/git", "/usr/local/bin/git", "git"]
            for path in common_paths:
                try:
                    subprocess.run([path, "--version"], capture_output=True, check=True)
                    return path
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            raise RuntimeError("Git executable not found on system")
    
    def _validate_repository(self) -> None:
        """Validate that the repo_path is a valid git repository"""
        if not os.path.exists(self.repo_path):
            raise ValueError(f"Repository path does not exist: {self.repo_path}")
        
        # Check if it's a git repository
        try:
            self._run_git_command(["rev-parse", "--git-dir"])
        except subprocess.CalledProcessError:
            raise ValueError(f"Not a git repository: {self.repo_path}")
    
    def _run_git_command(
        self, 
        args: List[str], 
        input_data: str = None,
        timeout: int = 30
    ) -> subprocess.CompletedProcess:
        """
        Run a git command and return the result.
        
        Args:
            args: Git command arguments
            input_data: Optional input data for the command
            timeout: Command timeout in seconds
            
        Returns:
            CompletedProcess result
            
        Raises:
            subprocess.CalledProcessError: If command fails
            subprocess.TimeoutExpired: If command times out
        """
        cmd = [self.git_executable] + args
        
        return subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            input=input_data,
            timeout=timeout,
            check=True
        )
    
    def _create_result(
        self, 
        success: bool, 
        message: str, 
        data: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        suggestions: List[str] = None,
        execution_time_ms: int = 0
    ) -> GitOperationResult:
        """Create a standardized GitOperationResult"""
        status = GitOperationStatus.SUCCESS if success else GitOperationStatus.FAILURE
        
        return GitOperationResult(
            success=success,
            status=status,
            message=message,
            data=data,
            provider_used="Standard Git",
            execution_time_ms=execution_time_ms,
            error_code=error_code,
            suggestions=suggestions or []
        )
    
    # Core Status and Information Methods
    
    def get_status(self) -> GitOperationResult:
        """Get comprehensive repository status"""
        start_time = time.time()
        
        try:
            # Get porcelain status
            result = self._run_git_command(["status", "--porcelain=v1"])
            
            # Parse status output
            files = self._parse_status_output(result.stdout)
            
            # Get current branch
            branch_result = self._run_git_command(["branch", "--show-current"])
            current_branch = branch_result.stdout.strip()
            
            # Get ahead/behind info if tracking branch exists
            ahead_behind = self._get_ahead_behind_counts(current_branch)
            
            # Check if working tree is clean
            is_clean = len(files) == 0
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return self._create_result(
                success=True,
                message=f"Repository status retrieved successfully. {'Clean' if is_clean else 'Has changes'}",
                data={
                    "clean": is_clean,
                    "files": [file.__dict__ for file in files],
                    "branch": current_branch,
                    "ahead_behind": ahead_behind,
                    "total_files": len(files),
                    "staged_files": len([f for f in files if f.staged]),
                    "modified_files": len([f for f in files if f.working_tree_status == "M" or (f.status == "M" and not f.staged)]),
                    "untracked_files": len([f for f in files if f.status == "??"])
                },
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            return self._create_result(
                success=False,
                message=f"Failed to get repository status: {e.stderr}",
                error_code="GIT_STATUS_FAILED",
                suggestions=[
                    "Ensure you're in a valid git repository",
                    "Check git installation and permissions"
                ],
                execution_time_ms=execution_time
            )
    
    def _parse_status_output(self, output: str) -> List[FileStatus]:
        """Parse git status --porcelain output into FileStatus objects"""
        files = []
        
        for line in output.strip().split('\n'):
            if not line:
                continue
            
            # Git status format: XY filename
            if len(line) < 3:
                continue
            
            index_status = line[0]
            working_tree_status = line[1]
            file_path = line[3:]  # Skip the space
            
            # Determine overall status
            if index_status == '?' and working_tree_status == '?':
                status = '??'  # Untracked
                staged = False
            elif index_status != ' ':
                status = index_status
                staged = True
            else:
                status = working_tree_status
                staged = False
            
            files.append(FileStatus(
                path=file_path,
                status=status,
                staged=staged,
                working_tree_status=working_tree_status,
                index_status=index_status
            ))
        
        return files
    
    def _get_ahead_behind_counts(self, branch: str) -> Dict[str, int]:
        """Get ahead/behind counts for current branch"""
        try:
            result = self._run_git_command([
                "rev-list", "--left-right", "--count", f"{branch}...@{{u}}"
            ])
            
            counts = result.stdout.strip().split('\t')
            if len(counts) == 2:
                return {
                    "ahead": int(counts[0]),
                    "behind": int(counts[1])
                }
        except subprocess.CalledProcessError:
            # No upstream branch or other error
            pass
        
        return {"ahead": 0, "behind": 0}
    
    def get_current_branch(self) -> GitOperationResult:
        """Get current branch information"""
        start_time = time.time()
        
        try:
            result = self._run_git_command(["branch", "--show-current"])
            branch_name = result.stdout.strip()
            
            if not branch_name:
                # Might be in detached HEAD state
                result = self._run_git_command(["rev-parse", "HEAD"])
                commit_hash = result.stdout.strip()
                branch_name = f"HEAD detached at {commit_hash[:7]}"
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return self._create_result(
                success=True,
                message=f"Current branch: {branch_name}",
                data={"branch": branch_name},
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            return self._create_result(
                success=False,
                message=f"Failed to get current branch: {e.stderr}",
                error_code="GIT_BRANCH_FAILED",
                execution_time_ms=execution_time
            )
    
    def list_branches(self, include_remote: bool = True) -> GitOperationResult:
        """List all branches with comprehensive metadata"""
        start_time = time.time()
        
        try:
            # Get local branches
            args = ["branch", "-vv"]
            if include_remote:
                args.append("--all")
            
            result = self._run_git_command(args)
            branches = self._parse_branch_output(result.stdout)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return self._create_result(
                success=True,
                message=f"Found {len(branches)} branches",
                data={
                    "branches": [branch.__dict__ for branch in branches],
                    "total_count": len(branches),
                    "local_count": len([b for b in branches if not b.name.startswith("remotes/")]),
                    "remote_count": len([b for b in branches if b.name.startswith("remotes/")])
                },
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            return self._create_result(
                success=False,
                message=f"Failed to list branches: {e.stderr}",
                error_code="GIT_BRANCH_LIST_FAILED",
                execution_time_ms=execution_time
            )
    
    def _parse_branch_output(self, output: str) -> List[BranchInfo]:
        """Parse git branch output into BranchInfo objects"""
        branches = []
        
        for line in output.strip().split('\n'):
            if not line.strip():
                continue
            
            # Parse branch line format: * branch_name commit_hash [tracking] commit_message
            is_current = line.startswith('*')
            line = line[2:] if is_current else line[2:]  # Remove marker and space
            
            parts = line.split()
            if len(parts) < 2:
                continue
            
            branch_name = parts[0]
            commit_hash = parts[1]
            
            # Extract tracking branch if present
            tracking_branch = None
            if '[' in line and ']' in line:
                tracking_match = re.search(r'\[([^\]]+)\]', line)
                if tracking_match:
                    tracking_info = tracking_match.group(1)
                    if ':' in tracking_info:
                        tracking_branch = tracking_info.split(':')[0]
                    else:
                        tracking_branch = tracking_info
            
            # Get commit message (everything after the tracking info)
            commit_message = ""
            bracket_end = line.find(']')
            if bracket_end != -1:
                commit_message = line[bracket_end + 1:].strip()
            else:
                # No tracking info, message starts after commit hash
                message_start = line.find(commit_hash) + len(commit_hash)
                commit_message = line[message_start:].strip()
            
            # Get detailed commit info
            commit_date, commit_author = self._get_commit_details(commit_hash)
            
            # Get ahead/behind counts
            ahead_behind = self._get_ahead_behind_counts(branch_name) if is_current else {"ahead": 0, "behind": 0}
            
            branches.append(BranchInfo(
                name=branch_name,
                is_current=is_current,
                ahead_count=ahead_behind["ahead"],
                behind_count=ahead_behind["behind"],
                last_commit_hash=commit_hash,
                last_commit_message=commit_message,
                last_commit_date=commit_date,
                last_commit_author=commit_author,
                tracking_branch=tracking_branch
            ))
        
        return branches
    
    def _get_commit_details(self, commit_hash: str) -> Tuple[datetime, str]:
        """Get commit date and author for a specific commit"""
        try:
            result = self._run_git_command([
                "show", "-s", "--format=%ci|%an", commit_hash
            ])
            
            parts = result.stdout.strip().split('|')
            if len(parts) == 2:
                date_str, author = parts
                commit_date = datetime.fromisoformat(date_str.replace(' ', 'T', 1))
                return commit_date, author
        except (subprocess.CalledProcessError, ValueError):
            pass
        
        return datetime.now(), "Unknown"
    
    # Branch Management Methods
    
    def create_branch(self, name: str, from_branch: str = "HEAD") -> GitOperationResult:
        """Create a new branch"""
        start_time = time.time()
        
        # Validate branch name
        if not self.validate_branch_name(name):
            return self._create_result(
                success=False,
                message=f"Invalid branch name: {name}",
                error_code="GIT_INVALID_BRANCH_NAME",
                suggestions=[
                    "Branch names cannot contain spaces or special characters",
                    "Use hyphens or underscores instead of spaces",
                    "Avoid starting with dots or ending with slashes"
                ]
            )
        
        try:
            self._run_git_command(["checkout", "-b", name, from_branch])
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return self._create_result(
                success=True,
                message=f"Created and switched to branch '{name}' from '{from_branch}'",
                data={
                    "branch_name": name,
                    "from_branch": from_branch,
                    "switched": True
                },
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            suggestions = ["Check if branch name already exists"]
            if "already exists" in e.stderr:
                suggestions.append(f"Use 'git checkout {name}' to switch to existing branch")
            
            return self._create_result(
                success=False,
                message=f"Failed to create branch '{name}': {e.stderr}",
                error_code="GIT_CREATE_BRANCH_FAILED",
                suggestions=suggestions,
                execution_time_ms=execution_time
            )
    
    def switch_branch(self, name: str, create_if_missing: bool = False) -> GitOperationResult:
        """Switch to a branch"""
        start_time = time.time()
        
        try:
            args = ["checkout"]
            if create_if_missing:
                args.append("-b")
            args.append(name)
            
            self._run_git_command(args)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            action = "Created and switched to" if create_if_missing else "Switched to"
            return self._create_result(
                success=True,
                message=f"{action} branch '{name}'",
                data={
                    "branch_name": name,
                    "created": create_if_missing
                },
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            suggestions = []
            if "did not match any file(s)" in e.stderr:
                suggestions.extend([
                    f"Branch '{name}' does not exist",
                    "Use create_if_missing=True to create the branch",
                    "Check available branches with list_branches()"
                ])
            
            return self._create_result(
                success=False,
                message=f"Failed to switch to branch '{name}': {e.stderr}",
                error_code="GIT_SWITCH_BRANCH_FAILED",
                suggestions=suggestions,
                execution_time_ms=execution_time
            )
    
    def delete_branch(self, name: str, force: bool = False) -> GitOperationResult:
        """Delete a branch"""
        start_time = time.time()
        
        try:
            args = ["branch"]
            args.append("-D" if force else "-d")
            args.append(name)
            
            self._run_git_command(args)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return self._create_result(
                success=True,
                message=f"Deleted branch '{name}'",
                data={
                    "branch_name": name,
                    "forced": force
                },
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            suggestions = []
            if "not fully merged" in e.stderr:
                suggestions.extend([
                    f"Branch '{name}' is not fully merged",
                    "Use force=True to delete anyway",
                    "Merge the branch first if you want to keep changes"
                ])
            
            return self._create_result(
                success=False,
                message=f"Failed to delete branch '{name}': {e.stderr}",
                error_code="GIT_DELETE_BRANCH_FAILED",
                suggestions=suggestions,
                execution_time_ms=execution_time
            )
    
    def merge_branch(self, source: str, target: str = None) -> GitOperationResult:
        """Merge branches"""
        start_time = time.time()
        
        try:
            # Switch to target branch if specified
            if target:
                switch_result = self.switch_branch(target)
                if not switch_result.success:
                    return switch_result
            
            # Perform merge
            self._run_git_command(["merge", source])
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return self._create_result(
                success=True,
                message=f"Successfully merged '{source}' into current branch",
                data={
                    "source_branch": source,
                    "target_branch": target,
                    "conflicts": False
                },
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            # Check if it's a merge conflict
            if "CONFLICT" in e.stdout or "Automatic merge failed" in e.stdout:
                conflicts = self.get_merge_conflicts()
                return GitOperationResult(
                    success=False,
                    status=GitOperationStatus.CONFLICT,
                    message=f"Merge conflicts detected when merging '{source}'",
                    data={
                        "source_branch": source,
                        "target_branch": target,
                        "conflicts": True,
                        "conflict_files": conflicts.data.get("conflicts", []) if conflicts.success else []
                    },
                    provider_used="Standard Git",
                    execution_time_ms=execution_time,
                    error_code="GIT_MERGE_CONFLICT",
                    suggestions=[
                        "Resolve conflicts manually",
                        "Use get_merge_conflicts() to see conflicted files",
                        "Run 'git add' after resolving conflicts",
                        "Complete merge with 'git commit'"
                    ]
                )
            
            return self._create_result(
                success=False,
                message=f"Failed to merge '{source}': {e.stderr}",
                error_code="GIT_MERGE_FAILED",
                execution_time_ms=execution_time
            )
    
    # Provider Capability Methods
    
    def is_available(self) -> bool:
        """Check if this provider is available and functional"""
        try:
            self._run_git_command(["--version"])
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, RuntimeError):
            return False
    
    def get_provider_name(self) -> str:
        """Get human-readable provider name"""
        return "Standard Git"
    
    def get_provider_capabilities(self) -> Dict[str, bool]:
        """Get provider-specific capabilities"""
        return {
            "branch_management": True,
            "commit_operations": True,
            "remote_operations": True,
            "conflict_resolution": True,
            "visual_merge_tools": False,  # Command-line only
            "enhanced_ui": False,
            "api_integration": False,
            "advanced_analytics": False
        }
    
    def get_health_status(self) -> GitOperationResult:
        """Get provider health status for monitoring"""
        start_time = time.time()
        
        try:
            # Check git version
            version_result = self._run_git_command(["--version"])
            git_version = version_result.stdout.strip()
            
            # Check repository status
            status_result = self._run_git_command(["status", "--porcelain"])
            
            # Check if we can access remote
            remote_accessible = True
            try:
                self._run_git_command(["ls-remote", "--heads", "origin"], timeout=5)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                remote_accessible = False
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return self._create_result(
                success=True,
                message="Standard Git provider is healthy",
                data={
                    "git_version": git_version,
                    "repository_accessible": True,
                    "remote_accessible": remote_accessible,
                    "git_executable": self.git_executable,
                    "repo_path": self.repo_path
                },
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            return self._create_result(
                success=False,
                message=f"Standard Git provider health check failed: {e.stderr}",
                error_code="GIT_HEALTH_CHECK_FAILED",
                execution_time_ms=execution_time
            )
    
    # Additional Branch Management Methods
    
    def get_branch_details(self, branch_name: str) -> GitOperationResult:
        """Get detailed information about a specific branch"""
        start_time = time.time()
        
        try:
            # Check if branch exists
            try:
                self._run_git_command(["show-ref", "--verify", f"refs/heads/{branch_name}"])
            except subprocess.CalledProcessError:
                return self._create_result(
                    success=False,
                    message=f"Branch '{branch_name}' does not exist",
                    error_code="GIT_BRANCH_NOT_FOUND",
                    suggestions=[
                        f"Check available branches with list_branches()",
                        f"Create branch with create_branch('{branch_name}')"
                    ]
                )
            
            # Get branch info
            result = self._run_git_command([
                "show", "--format=%H|%h|%s|%an|%ae|%ci", "--no-patch", branch_name
            ])
            
            commit_info = result.stdout.strip().split('|')
            if len(commit_info) >= 6:
                commit_hash = commit_info[0]
                short_hash = commit_info[1]
                commit_message = commit_info[2]
                author_name = commit_info[3]
                author_email = commit_info[4]
                commit_date_str = commit_info[5]
                
                try:
                    commit_date = datetime.fromisoformat(commit_date_str.replace(' ', 'T', 1))
                except ValueError:
                    commit_date = datetime.now()
            else:
                return self._create_result(
                    success=False,
                    message=f"Failed to parse branch information for '{branch_name}'",
                    error_code="GIT_BRANCH_INFO_PARSE_FAILED"
                )
            
            # Get tracking branch info
            tracking_branch = None
            try:
                tracking_result = self._run_git_command([
                    "config", f"branch.{branch_name}.remote"
                ])
                remote = tracking_result.stdout.strip()
                
                merge_result = self._run_git_command([
                    "config", f"branch.{branch_name}.merge"
                ])
                merge_ref = merge_result.stdout.strip()
                
                if remote and merge_ref:
                    # Extract branch name from refs/heads/branch_name
                    remote_branch = merge_ref.replace("refs/heads/", "")
                    tracking_branch = f"{remote}/{remote_branch}"
            except subprocess.CalledProcessError:
                pass  # No tracking branch
            
            # Get ahead/behind counts if tracking branch exists
            ahead_behind = {"ahead": 0, "behind": 0}
            if tracking_branch:
                ahead_behind = self._get_ahead_behind_counts(branch_name)
            
            # Check if branch is current
            current_branch_result = self._run_git_command(["branch", "--show-current"])
            is_current = current_branch_result.stdout.strip() == branch_name
            
            execution_time = int((time.time() - start_time) * 1000)
            
            branch_details = BranchInfo(
                name=branch_name,
                is_current=is_current,
                ahead_count=ahead_behind["ahead"],
                behind_count=ahead_behind["behind"],
                last_commit_hash=commit_hash,
                last_commit_message=commit_message,
                last_commit_date=commit_date,
                last_commit_author=author_name,
                tracking_branch=tracking_branch
            )
            
            return self._create_result(
                success=True,
                message=f"Retrieved details for branch '{branch_name}'",
                data={
                    "branch": branch_details.__dict__,
                    "commit_hash": commit_hash,
                    "short_hash": short_hash,
                    "author_email": author_email,
                    "tracking_branch": tracking_branch,
                    "ahead_count": ahead_behind["ahead"],
                    "behind_count": ahead_behind["behind"]
                },
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            return self._create_result(
                success=False,
                message=f"Failed to get branch details for '{branch_name}': {e.stderr}",
                error_code="GIT_BRANCH_DETAILS_FAILED",
                execution_time_ms=execution_time
            )
    
    def rename_branch(self, old_name: str, new_name: str) -> GitOperationResult:
        """Rename a branch"""
        start_time = time.time()
        
        # Validate new branch name
        if not self.validate_branch_name(new_name):
            return self._create_result(
                success=False,
                message=f"Invalid new branch name: {new_name}",
                error_code="GIT_INVALID_BRANCH_NAME",
                suggestions=[
                    "Branch names cannot contain spaces or special characters",
                    "Use hyphens or underscores instead of spaces"
                ]
            )
        
        try:
            # Check if old branch exists
            try:
                self._run_git_command(["show-ref", "--verify", f"refs/heads/{old_name}"])
            except subprocess.CalledProcessError:
                return self._create_result(
                    success=False,
                    message=f"Branch '{old_name}' does not exist",
                    error_code="GIT_BRANCH_NOT_FOUND",
                    suggestions=[f"Check available branches with list_branches()"]
                )
            
            # Rename the branch
            self._run_git_command(["branch", "-m", old_name, new_name])
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return self._create_result(
                success=True,
                message=f"Renamed branch '{old_name}' to '{new_name}'",
                data={
                    "old_name": old_name,
                    "new_name": new_name
                },
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            suggestions = []
            if "already exists" in e.stderr:
                suggestions.append(f"Branch '{new_name}' already exists")
                suggestions.append("Choose a different name or delete the existing branch first")
            
            return self._create_result(
                success=False,
                message=f"Failed to rename branch '{old_name}' to '{new_name}': {e.stderr}",
                error_code="GIT_RENAME_BRANCH_FAILED",
                suggestions=suggestions,
                execution_time_ms=execution_time
            )
    
    def set_upstream_branch(self, branch_name: str, upstream: str) -> GitOperationResult:
        """Set upstream tracking branch"""
        start_time = time.time()
        
        try:
            # Set upstream branch
            self._run_git_command(["branch", "--set-upstream-to", upstream, branch_name])
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return self._create_result(
                success=True,
                message=f"Set upstream for '{branch_name}' to '{upstream}'",
                data={
                    "branch_name": branch_name,
                    "upstream": upstream
                },
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            suggestions = []
            if "does not exist" in e.stderr:
                suggestions.extend([
                    f"Upstream branch '{upstream}' does not exist",
                    "Check available remote branches",
                    "Fetch from remote first if needed"
                ])
            
            return self._create_result(
                success=False,
                message=f"Failed to set upstream for '{branch_name}': {e.stderr}",
                error_code="GIT_SET_UPSTREAM_FAILED",
                suggestions=suggestions,
                execution_time_ms=execution_time
            )
    
    def unset_upstream_branch(self, branch_name: str) -> GitOperationResult:
        """Unset upstream tracking branch"""
        start_time = time.time()
        
        try:
            # Unset upstream branch
            self._run_git_command(["branch", "--unset-upstream", branch_name])
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return self._create_result(
                success=True,
                message=f"Unset upstream for branch '{branch_name}'",
                data={"branch_name": branch_name},
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            suggestions = []
            if "no upstream" in e.stderr.lower():
                suggestions.append(f"Branch '{branch_name}' has no upstream branch set")
            
            return self._create_result(
                success=False,
                message=f"Failed to unset upstream for '{branch_name}': {e.stderr}",
                error_code="GIT_UNSET_UPSTREAM_FAILED",
                suggestions=suggestions,
                execution_time_ms=execution_time
            )
    
    def compare_branches(self, branch1: str, branch2: str) -> GitOperationResult:
        """Compare two branches and show differences"""
        start_time = time.time()
        
        try:
            # Get commit counts between branches
            ahead_result = self._run_git_command([
                "rev-list", "--count", f"{branch2}..{branch1}"
            ])
            ahead_count = int(ahead_result.stdout.strip())
            
            behind_result = self._run_git_command([
                "rev-list", "--count", f"{branch1}..{branch2}"
            ])
            behind_count = int(behind_result.stdout.strip())
            
            # Get list of commits unique to each branch
            commits_ahead = []
            if ahead_count > 0:
                commits_ahead_result = self._run_git_command([
                    "log", "--format=%H|%s|%an|%ci", f"{branch2}..{branch1}"
                ])
                for line in commits_ahead_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 4:
                            commits_ahead.append({
                                "hash": parts[0],
                                "message": parts[1],
                                "author": parts[2],
                                "date": parts[3]
                            })
            
            commits_behind = []
            if behind_count > 0:
                commits_behind_result = self._run_git_command([
                    "log", "--format=%H|%s|%an|%ci", f"{branch1}..{branch2}"
                ])
                for line in commits_behind_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 4:
                            commits_behind.append({
                                "hash": parts[0],
                                "message": parts[1],
                                "author": parts[2],
                                "date": parts[3]
                            })
            
            # Determine relationship
            if ahead_count == 0 and behind_count == 0:
                relationship = "identical"
            elif ahead_count > 0 and behind_count == 0:
                relationship = f"{branch1} is ahead"
            elif ahead_count == 0 and behind_count > 0:
                relationship = f"{branch1} is behind"
            else:
                relationship = "diverged"
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return self._create_result(
                success=True,
                message=f"Compared branches '{branch1}' and '{branch2}': {relationship}",
                data={
                    "branch1": branch1,
                    "branch2": branch2,
                    "relationship": relationship,
                    "ahead_count": ahead_count,
                    "behind_count": behind_count,
                    "commits_ahead": commits_ahead,
                    "commits_behind": commits_behind,
                    "can_fast_forward": behind_count == 0 and ahead_count > 0
                },
                execution_time_ms=execution_time
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            suggestions = []
            if "unknown revision" in e.stderr:
                suggestions.extend([
                    "One or both branches do not exist",
                    "Check branch names with list_branches()"
                ])
            
            return self._create_result(
                success=False,
                message=f"Failed to compare branches '{branch1}' and '{branch2}': {e.stderr}",
                error_code="GIT_COMPARE_BRANCHES_FAILED",
                suggestions=suggestions,
                execution_time_ms=execution_time
            )
    
    # Placeholder methods for remaining interface (to be implemented in subsequent tasks)
    
    def stage_files(self, files: List[str] = None) -> GitOperationResult:
        """Stage files for commit - placeholder for next task"""
        return self._create_result(
            success=False,
            message="stage_files not yet implemented",
            error_code="NOT_IMPLEMENTED"
        )
    
    def unstage_files(self, files: List[str] = None) -> GitOperationResult:
        """Unstage files - placeholder for next task"""
        return self._create_result(
            success=False,
            message="unstage_files not yet implemented",
            error_code="NOT_IMPLEMENTED"
        )
    
    def commit_changes(self, message: str, files: List[str] = None) -> GitOperationResult:
        """Commit staged changes - placeholder for next task"""
        return self._create_result(
            success=False,
            message="commit_changes not yet implemented",
            error_code="NOT_IMPLEMENTED"
        )
    
    def get_commit_history(self, branch: str = None, limit: int = 50) -> GitOperationResult:
        """Get commit history - placeholder for next task"""
        return self._create_result(
            success=False,
            message="get_commit_history not yet implemented",
            error_code="NOT_IMPLEMENTED"
        )
    
    def push_changes(self, branch: str = None, remote: str = "origin") -> GitOperationResult:
        """Push changes to remote - placeholder for next task"""
        return self._create_result(
            success=False,
            message="push_changes not yet implemented",
            error_code="NOT_IMPLEMENTED"
        )
    
    def pull_changes(self, branch: str = None, remote: str = "origin") -> GitOperationResult:
        """Pull changes from remote - placeholder for next task"""
        return self._create_result(
            success=False,
            message="pull_changes not yet implemented",
            error_code="NOT_IMPLEMENTED"
        )
    
    def fetch_changes(self, remote: str = "origin") -> GitOperationResult:
        """Fetch changes from remote - placeholder for next task"""
        return self._create_result(
            success=False,
            message="fetch_changes not yet implemented",
            error_code="NOT_IMPLEMENTED"
        )
    
    def get_merge_conflicts(self) -> GitOperationResult:
        """Get merge conflicts - placeholder for next task"""
        return self._create_result(
            success=False,
            message="get_merge_conflicts not yet implemented",
            error_code="NOT_IMPLEMENTED"
        )
    
    def resolve_conflict(self, file_path: str, resolution: str) -> GitOperationResult:
        """Resolve merge conflict - placeholder for next task"""
        return self._create_result(
            success=False,
            message="resolve_conflict not yet implemented",
            error_code="NOT_IMPLEMENTED"
        )