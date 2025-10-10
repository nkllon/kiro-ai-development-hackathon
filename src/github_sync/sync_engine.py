"""
Synchronization engine for GitHub data.

This module provides the core synchronization logic for keeping local data
in sync with GitHub repositories, issues, pull requests, and commits.
"""

import logging
import time
from typing import Optional, List, Dict, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json

from .models import (
    Repository, Issue, PullRequest, Commit, SyncResult, DataConflict, 
    ConflictResolution, IssueState, PullRequestState
)
from .client import GitHubAPIClient, GitHubAPIError, RateLimitError
from .config import RepositoryConfig, SyncConfig, ConflictResolutionStrategy
from .auth import AuthenticationManager

logger = logging.getLogger(__name__)


@dataclass
class SyncState:
    """Represents the synchronization state for a repository."""
    repository_id: str
    last_sync_time: Optional[datetime] = None
    last_issue_sync: Optional[datetime] = None
    last_pr_sync: Optional[datetime] = None
    last_commit_sync: Optional[datetime] = None
    sync_in_progress: bool = False
    error_count: int = 0
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert sync state to dictionary for persistence."""
        return {
            'repository_id': self.repository_id,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'last_issue_sync': self.last_issue_sync.isoformat() if self.last_issue_sync else None,
            'last_pr_sync': self.last_pr_sync.isoformat() if self.last_pr_sync else None,
            'last_commit_sync': self.last_commit_sync.isoformat() if self.last_commit_sync else None,
            'sync_in_progress': self.sync_in_progress,
            'error_count': self.error_count,
            'last_error': self.last_error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncState':
        """Create sync state from dictionary."""
        return cls(
            repository_id=data['repository_id'],
            last_sync_time=datetime.fromisoformat(data['last_sync_time']) if data.get('last_sync_time') else None,
            last_issue_sync=datetime.fromisoformat(data['last_issue_sync']) if data.get('last_issue_sync') else None,
            last_pr_sync=datetime.fromisoformat(data['last_pr_sync']) if data.get('last_pr_sync') else None,
            last_commit_sync=datetime.fromisoformat(data['last_commit_sync']) if data.get('last_commit_sync') else None,
            sync_in_progress=data.get('sync_in_progress', False),
            error_count=data.get('error_count', 0),
            last_error=data.get('last_error')
        )


class ChangeDetector:
    """Detects changes in GitHub data using checksums and timestamps."""
    
    def __init__(self):
        self.checksums: Dict[str, str] = {}
    
    def calculate_checksum(self, data: Any) -> str:
        """Calculate checksum for data object."""
        if hasattr(data, '__dict__'):
            # For dataclass objects
            data_dict = data.__dict__.copy()
            # Remove timestamp fields that change frequently
            data_dict.pop('last_sync', None)
            data_dict.pop('updated_at', None)
            data_str = json.dumps(data_dict, sort_keys=True, default=str)
        else:
            data_str = json.dumps(data, sort_keys=True, default=str)
        
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def has_changed(self, key: str, data: Any) -> bool:
        """Check if data has changed since last check."""
        current_checksum = self.calculate_checksum(data)
        previous_checksum = self.checksums.get(key)
        
        if previous_checksum != current_checksum:
            self.checksums[key] = current_checksum
            return True
        
        return False
    
    def mark_synced(self, key: str, data: Any) -> None:
        """Mark data as synced by storing its checksum."""
        self.checksums[key] = self.calculate_checksum(data)


class ConflictResolver:
    """Handles data synchronization conflicts."""
    
    def __init__(self, strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MANUAL):
        self.strategy = strategy
        self.pending_conflicts: List[DataConflict] = []
    
    def detect_conflict(self, entity_type: str, entity_id: str, 
                       local_data: Dict[str, Any], remote_data: Dict[str, Any]) -> Optional[DataConflict]:
        """Detect conflicts between local and remote data."""
        conflict_fields = []
        
        # Compare all fields
        all_fields = set(local_data.keys()) | set(remote_data.keys())
        
        for field in all_fields:
            local_value = local_data.get(field)
            remote_value = remote_data.get(field)
            
            # Skip timestamp fields for conflict detection
            if field in ['updated_at', 'last_sync', 'created_at']:
                continue
            
            if local_value != remote_value:
                conflict_fields.append(field)
        
        if conflict_fields:
            return DataConflict(
                entity_type=entity_type,
                entity_id=entity_id,
                local_data=local_data,
                remote_data=remote_data,
                conflict_fields=conflict_fields
            )
        
        return None
    
    def resolve_conflict(self, conflict: DataConflict) -> Dict[str, Any]:
        """Resolve a data conflict based on the configured strategy."""
        if self.strategy == ConflictResolutionStrategy.REMOTE_WINS:
            return conflict.remote_data
        elif self.strategy == ConflictResolutionStrategy.LOCAL_WINS:
            return conflict.local_data
        elif self.strategy == ConflictResolutionStrategy.LAST_MODIFIED_WINS:
            # Use the data with the most recent update timestamp
            local_updated = conflict.local_data.get('updated_at')
            remote_updated = conflict.remote_data.get('updated_at')
            
            if local_updated and remote_updated:
                if isinstance(local_updated, str):
                    local_updated = datetime.fromisoformat(local_updated.replace('Z', '+00:00'))
                if isinstance(remote_updated, str):
                    remote_updated = datetime.fromisoformat(remote_updated.replace('Z', '+00:00'))
                
                return conflict.remote_data if remote_updated > local_updated else conflict.local_data
            else:
                return conflict.remote_data  # Default to remote if timestamps unavailable
        else:
            # Manual resolution - add to pending conflicts
            self.pending_conflicts.append(conflict)
            return conflict.local_data  # Keep local data until manual resolution


class SynchronizationEngine:
    """
    Core synchronization engine for GitHub data.
    
    This engine orchestrates the synchronization process between GitHub and local storage,
    managing data consistency, conflict resolution, and incremental updates.
    """
    
    def __init__(self, github_client: Optional[GitHubAPIClient] = None, 
                 sync_config: Optional[SyncConfig] = None):
        """
        Initialize the synchronization engine.
        
        Args:
            github_client: GitHub API client instance
            sync_config: Synchronization configuration
        """
        self.github_client = github_client or GitHubAPIClient()
        self.sync_config = sync_config or SyncConfig()
        self.change_detector = ChangeDetector()
        self.conflict_resolver = ConflictResolver(self.sync_config.conflict_resolution)
        self.sync_states: Dict[str, SyncState] = {}
        
        # Thread pool for concurrent synchronization
        self.executor = ThreadPoolExecutor(max_workers=self.sync_config.max_concurrent_syncs)
    
    def sync_repository(self, repo_config: RepositoryConfig) -> SyncResult:
        """
        Synchronize a single repository.
        
        Args:
            repo_config: Repository configuration
            
        Returns:
            Synchronization result
        """
        repo_id = repo_config.full_name
        sync_state = self.sync_states.get(repo_id, SyncState(repo_id))
        
        if sync_state.sync_in_progress:
            logger.warning(f"Sync already in progress for {repo_id}")
            return SyncResult(success=False, errors=[f"Sync already in progress for {repo_id}"])
        
        sync_state.sync_in_progress = True
        self.sync_states[repo_id] = sync_state
        
        start_time = time.time()
        result = SyncResult(success=True, last_sync_time=datetime.utcnow())
        
        try:
            logger.info(f"Starting synchronization for repository {repo_id}")
            
            # Sync repository metadata
            repo_result = self._sync_repository_metadata(repo_config)
            result = result.merge(repo_result)
            
            # Sync issues if enabled
            if repo_config.sync_issues:
                issues_result = self._sync_issues(repo_config, sync_state)
                result = result.merge(issues_result)
            
            # Sync pull requests if enabled
            if repo_config.sync_pull_requests:
                prs_result = self._sync_pull_requests(repo_config, sync_state)
                result = result.merge(prs_result)
            
            # Sync commits if enabled
            if repo_config.sync_commits:
                commits_result = self._sync_commits(repo_config, sync_state)
                result = result.merge(commits_result)
            
            # Update sync state
            sync_state.last_sync_time = datetime.utcnow()
            sync_state.error_count = 0 if result.success else sync_state.error_count + 1
            sync_state.last_error = result.errors[0] if result.errors else None
            
            logger.info(f"Completed synchronization for {repo_id}: {result.items_synced} items synced")
            
        except Exception as e:
            logger.error(f"Synchronization failed for {repo_id}: {e}")
            result.add_error(f"Synchronization failed: {e}")
            sync_state.error_count += 1
            sync_state.last_error = str(e)
        
        finally:
            sync_state.sync_in_progress = False
            result.sync_duration = time.time() - start_time
        
        return result
    
    def _sync_repository_metadata(self, repo_config: RepositoryConfig) -> SyncResult:
        """Synchronize repository metadata."""
        result = SyncResult(success=True)
        
        try:
            # Fetch repository data from GitHub
            repo = self.github_client.get_repository(repo_config.owner, repo_config.name)
            
            # Check if repository data has changed
            repo_key = f"repo:{repo_config.full_name}"
            if self.change_detector.has_changed(repo_key, repo):
                # Repository data has changed - update local storage
                # This would typically involve database operations
                logger.info(f"Repository metadata updated for {repo_config.full_name}")
                result.items_updated += 1
                result.items_synced += 1
                
                self.change_detector.mark_synced(repo_key, repo)
            
        except Exception as e:
            logger.error(f"Failed to sync repository metadata for {repo_config.full_name}: {e}")
            result.add_error(f"Repository metadata sync failed: {e}")
        
        return result
    
    def _sync_issues(self, repo_config: RepositoryConfig, sync_state: SyncState) -> SyncResult:
        """Synchronize repository issues with bidirectional sync support."""
        result = SyncResult(success=True)
        
        try:
            # Determine sync strategy
            state_filter = "all" if repo_config.include_closed_issues else "open"
            
            # Fetch issues from GitHub
            issues = self.github_client.list_issues(
                repo_config.owner, 
                repo_config.name, 
                state=state_filter
            )
            
            # Track processed issues for bidirectional sync
            processed_issue_numbers = set()
            
            for issue in issues:
                issue_key = f"issue:{repo_config.full_name}:{issue.number}"
                processed_issue_numbers.add(issue.number)
                
                if self.change_detector.has_changed(issue_key, issue):
                    # Check for conflicts with local data
                    local_issue_data = self._get_local_issue_data(repo_config.full_name, issue.number)
                    if local_issue_data:
                        conflict = self.conflict_resolver.detect_conflict(
                            "issue", 
                            f"{repo_config.full_name}:{issue.number}",
                            local_issue_data,
                            issue.__dict__
                        )
                        
                        if conflict:
                            logger.warning(f"Conflict detected for issue #{issue.number} in {repo_config.full_name}")
                            resolved_data = self.conflict_resolver.resolve_conflict(conflict)
                            # Apply resolved data (would typically update database)
                            result.add_warning(f"Conflict resolved for issue #{issue.number}")
                    
                    # Issue has changed - update local storage
                    logger.debug(f"Issue #{issue.number} updated in {repo_config.full_name}")
                    result.items_updated += 1
                    result.items_synced += 1
                    
                    # Sync issue comments if needed
                    comments_result = self._sync_issue_comments(repo_config, issue.number)
                    result = result.merge(comments_result)
                    
                    # Sync labels and milestones
                    labels_result = self._sync_issue_labels(repo_config, issue)
                    result = result.merge(labels_result)
                    
                    self.change_detector.mark_synced(issue_key, issue)
            
            # Check for local issues that need to be pushed to GitHub (bidirectional sync)
            local_issues_result = self._sync_local_issues_to_github(repo_config, processed_issue_numbers)
            result = result.merge(local_issues_result)
            
            sync_state.last_issue_sync = datetime.utcnow()
            logger.info(f"Synced {len(issues)} issues for {repo_config.full_name}")
            
        except Exception as e:
            logger.error(f"Failed to sync issues for {repo_config.full_name}: {e}")
            result.add_error(f"Issues sync failed: {e}")
        
        return result
    
    def _sync_issue_comments(self, repo_config: RepositoryConfig, issue_number: int) -> SyncResult:
        """Synchronize comments for a specific issue."""
        result = SyncResult(success=True)
        
        try:
            # This would typically fetch comments from GitHub API
            # For now, we'll simulate the process
            logger.debug(f"Syncing comments for issue #{issue_number} in {repo_config.full_name}")
            
            # Placeholder for comment synchronization logic
            # Would involve:
            # 1. Fetch comments from GitHub
            # 2. Compare with local comments
            # 3. Update local storage
            # 4. Handle comment attribution and formatting
            
            result.items_synced += 1
            
        except Exception as e:
            logger.error(f"Failed to sync comments for issue #{issue_number}: {e}")
            result.add_error(f"Comment sync failed: {e}")
        
        return result
    
    def _sync_issue_labels(self, repo_config: RepositoryConfig, issue: Issue) -> SyncResult:
        """Synchronize labels and milestones for an issue."""
        result = SyncResult(success=True)
        
        try:
            # Sync labels
            for label in issue.labels:
                label_key = f"label:{repo_config.full_name}:{label}"
                # Check if label exists locally, create if needed
                logger.debug(f"Syncing label '{label}' for {repo_config.full_name}")
            
            # Sync milestone if present
            if issue.milestone:
                milestone_key = f"milestone:{repo_config.full_name}:{issue.milestone}"
                logger.debug(f"Syncing milestone '{issue.milestone}' for {repo_config.full_name}")
            
            result.items_synced += 1
            
        except Exception as e:
            logger.error(f"Failed to sync labels for issue #{issue.number}: {e}")
            result.add_error(f"Label sync failed: {e}")
        
        return result
    
    def _sync_local_issues_to_github(self, repo_config: RepositoryConfig, processed_issues: Set[int]) -> SyncResult:
        """Sync local issues that haven't been processed from GitHub (bidirectional sync)."""
        result = SyncResult(success=True)
        
        try:
            # This would typically:
            # 1. Get all local issues for the repository
            # 2. Find issues not in processed_issues set
            # 3. Push new/updated local issues to GitHub
            # 4. Handle any conflicts or errors
            
            # Placeholder for bidirectional sync logic
            logger.debug(f"Checking for local issues to sync to GitHub for {repo_config.full_name}")
            
        except Exception as e:
            logger.error(f"Failed to sync local issues to GitHub for {repo_config.full_name}: {e}")
            result.add_error(f"Local to GitHub sync failed: {e}")
        
        return result
    
    def _get_local_issue_data(self, repo_full_name: str, issue_number: int) -> Optional[Dict[str, Any]]:
        """Get local issue data for conflict detection."""
        # Placeholder - would typically query local database
        # Returns None if no local data exists
        return None
    
    def _sync_pull_requests(self, repo_config: RepositoryConfig, sync_state: SyncState) -> SyncResult:
        """Synchronize repository pull requests with bidirectional sync and review support."""
        result = SyncResult(success=True)
        
        try:
            # Determine sync strategy
            state_filter = "all" if repo_config.include_merged_prs else "open"
            
            # Fetch pull requests from GitHub
            pull_requests = self.github_client.list_pull_requests(
                repo_config.owner, 
                repo_config.name, 
                state=state_filter
            )
            
            # Track processed PRs for bidirectional sync
            processed_pr_numbers = set()
            
            for pr in pull_requests:
                pr_key = f"pr:{repo_config.full_name}:{pr.number}"
                processed_pr_numbers.add(pr.number)
                
                if self.change_detector.has_changed(pr_key, pr):
                    # Check for conflicts with local data
                    local_pr_data = self._get_local_pr_data(repo_config.full_name, pr.number)
                    if local_pr_data:
                        conflict = self.conflict_resolver.detect_conflict(
                            "pull_request", 
                            f"{repo_config.full_name}:{pr.number}",
                            local_pr_data,
                            pr.__dict__
                        )
                        
                        if conflict:
                            logger.warning(f"Conflict detected for PR #{pr.number} in {repo_config.full_name}")
                            resolved_data = self.conflict_resolver.resolve_conflict(conflict)
                            result.add_warning(f"Conflict resolved for PR #{pr.number}")
                    
                    # Pull request has changed - update local storage
                    logger.debug(f"Pull request #{pr.number} updated in {repo_config.full_name}")
                    result.items_updated += 1
                    result.items_synced += 1
                    
                    # Sync PR comments and reviews
                    comments_result = self._sync_pr_comments(repo_config, pr.number)
                    result = result.merge(comments_result)
                    
                    # Sync PR reviews
                    reviews_result = self._sync_pr_reviews(repo_config, pr.number)
                    result = result.merge(reviews_result)
                    
                    # Sync PR labels and assignees
                    metadata_result = self._sync_pr_metadata(repo_config, pr)
                    result = result.merge(metadata_result)
                    
                    self.change_detector.mark_synced(pr_key, pr)
            
            # Check for local PRs that need to be pushed to GitHub (bidirectional sync)
            local_prs_result = self._sync_local_prs_to_github(repo_config, processed_pr_numbers)
            result = result.merge(local_prs_result)
            
            sync_state.last_pr_sync = datetime.utcnow()
            logger.info(f"Synced {len(pull_requests)} pull requests for {repo_config.full_name}")
            
        except Exception as e:
            logger.error(f"Failed to sync pull requests for {repo_config.full_name}: {e}")
            result.add_error(f"Pull requests sync failed: {e}")
        
        return result
    
    def _sync_pr_comments(self, repo_config: RepositoryConfig, pr_number: int) -> SyncResult:
        """Synchronize comments for a specific pull request."""
        result = SyncResult(success=True)
        
        try:
            # This would typically fetch PR comments from GitHub API
            logger.debug(f"Syncing comments for PR #{pr_number} in {repo_config.full_name}")
            
            # Placeholder for PR comment synchronization logic
            # Would involve:
            # 1. Fetch PR comments from GitHub
            # 2. Fetch review comments (inline comments)
            # 3. Compare with local comments
            # 4. Update local storage with proper attribution
            # 5. Handle comment threading and replies
            
            result.items_synced += 1
            
        except Exception as e:
            logger.error(f"Failed to sync comments for PR #{pr_number}: {e}")
            result.add_error(f"PR comment sync failed: {e}")
        
        return result
    
    def _sync_pr_reviews(self, repo_config: RepositoryConfig, pr_number: int) -> SyncResult:
        """Synchronize reviews for a specific pull request."""
        result = SyncResult(success=True)
        
        try:
            # This would typically fetch PR reviews from GitHub API
            logger.debug(f"Syncing reviews for PR #{pr_number} in {repo_config.full_name}")
            
            # Placeholder for PR review synchronization logic
            # Would involve:
            # 1. Fetch PR reviews from GitHub
            # 2. Get review status (approved, changes_requested, commented)
            # 3. Sync reviewer assignments
            # 4. Update local storage with review state
            # 5. Handle review dismissals and re-reviews
            
            result.items_synced += 1
            
        except Exception as e:
            logger.error(f"Failed to sync reviews for PR #{pr_number}: {e}")
            result.add_error(f"PR review sync failed: {e}")
        
        return result
    
    def _sync_pr_metadata(self, repo_config: RepositoryConfig, pr: PullRequest) -> SyncResult:
        """Synchronize metadata (labels, assignees, reviewers) for a pull request."""
        result = SyncResult(success=True)
        
        try:
            # Sync labels
            for label in pr.labels:
                label_key = f"label:{repo_config.full_name}:{label}"
                logger.debug(f"Syncing label '{label}' for PR #{pr.number}")
            
            # Sync assignees
            for assignee in pr.assignees:
                logger.debug(f"Syncing assignee '{assignee}' for PR #{pr.number}")
            
            # Sync reviewers
            for reviewer in pr.reviewers:
                logger.debug(f"Syncing reviewer '{reviewer}' for PR #{pr.number}")
            
            result.items_synced += 1
            
        except Exception as e:
            logger.error(f"Failed to sync metadata for PR #{pr.number}: {e}")
            result.add_error(f"PR metadata sync failed: {e}")
        
        return result
    
    def _sync_local_prs_to_github(self, repo_config: RepositoryConfig, processed_prs: Set[int]) -> SyncResult:
        """Sync local PRs that haven't been processed from GitHub (bidirectional sync)."""
        result = SyncResult(success=True)
        
        try:
            # This would typically:
            # 1. Get all local PRs for the repository
            # 2. Find PRs not in processed_prs set
            # 3. Push new/updated local PRs to GitHub
            # 4. Handle any conflicts or errors
            
            # Placeholder for bidirectional sync logic
            logger.debug(f"Checking for local PRs to sync to GitHub for {repo_config.full_name}")
            
        except Exception as e:
            logger.error(f"Failed to sync local PRs to GitHub for {repo_config.full_name}: {e}")
            result.add_error(f"Local PR to GitHub sync failed: {e}")
        
        return result
    
    def _get_local_pr_data(self, repo_full_name: str, pr_number: int) -> Optional[Dict[str, Any]]:
        """Get local pull request data for conflict detection."""
        # Placeholder - would typically query local database
        # Returns None if no local data exists
        return None
    
    def _sync_commits(self, repo_config: RepositoryConfig, sync_state: SyncState) -> SyncResult:
        """Synchronize repository commits with branch tracking and merge event detection."""
        result = SyncResult(success=True)
        
        try:
            # First, sync branch information
            branches_result = self._sync_branches(repo_config)
            result = result.merge(branches_result)
            
            # Sync commits for each configured branch
            for branch in repo_config.sync_branches:
                try:
                    # Determine incremental sync parameters
                    since_date = None
                    if sync_state.last_commit_sync and repo_config.sync_strategy.value == "incremental":
                        since_date = sync_state.last_commit_sync.isoformat()
                    
                    # Fetch commits from GitHub
                    commits = self.github_client.get_commits(
                        repo_config.owner, 
                        repo_config.name, 
                        branch=branch,
                        per_page=repo_config.max_commits_per_sync,
                        since=since_date
                    )
                    
                    # Track merge events
                    merge_events = []
                    
                    for commit in commits:
                        commit_key = f"commit:{repo_config.full_name}:{commit.sha}"
                        
                        if self.change_detector.has_changed(commit_key, commit):
                            # Commit has changed - update local storage
                            logger.debug(f"Commit {commit.sha[:8]} updated in {repo_config.full_name}:{branch}")
                            result.items_updated += 1
                            result.items_synced += 1
                            
                            # Detect merge events
                            if len(commit.parents) > 1:
                                merge_event = self._analyze_merge_commit(repo_config, commit)
                                if merge_event:
                                    merge_events.append(merge_event)
                            
                            # Sync commit relationships
                            relationships_result = self._sync_commit_relationships(repo_config, commit)
                            result = result.merge(relationships_result)
                            
                            self.change_detector.mark_synced(commit_key, commit)
                    
                    # Process merge events
                    if merge_events:
                        merge_result = self._process_merge_events(repo_config, branch, merge_events)
                        result = result.merge(merge_result)
                    
                    logger.info(f"Synced {len(commits)} commits for {repo_config.full_name}:{branch}")
                    
                except Exception as e:
                    logger.error(f"Failed to sync commits for branch {branch} in {repo_config.full_name}: {e}")
                    result.add_error(f"Commits sync failed for branch {branch}: {e}")
            
            sync_state.last_commit_sync = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to sync commits for {repo_config.full_name}: {e}")
            result.add_error(f"Commits sync failed: {e}")
        
        return result
    
    def _sync_branches(self, repo_config: RepositoryConfig) -> SyncResult:
        """Synchronize branch information and state."""
        result = SyncResult(success=True)
        
        try:
            # Fetch all branches from GitHub
            branches = self.github_client.list_branches(repo_config.owner, repo_config.name)
            
            for branch_info in branches:
                branch_key = f"branch:{repo_config.full_name}:{branch_info['name']}"
                
                if self.change_detector.has_changed(branch_key, branch_info):
                    logger.debug(f"Branch '{branch_info['name']}' updated in {repo_config.full_name}")
                    result.items_updated += 1
                    result.items_synced += 1
                    
                    # Sync branch protection if applicable
                    if branch_info.get('protected'):
                        protection_result = self._sync_branch_protection(repo_config, branch_info['name'])
                        result = result.merge(protection_result)
                    
                    self.change_detector.mark_synced(branch_key, branch_info)
            
            logger.info(f"Synced {len(branches)} branches for {repo_config.full_name}")
            
        except Exception as e:
            logger.error(f"Failed to sync branches for {repo_config.full_name}: {e}")
            result.add_error(f"Branch sync failed: {e}")
        
        return result
    
    def _sync_branch_protection(self, repo_config: RepositoryConfig, branch_name: str) -> SyncResult:
        """Synchronize branch protection settings."""
        result = SyncResult(success=True)
        
        try:
            protection_info = self.github_client.get_branch_protection(
                repo_config.owner, 
                repo_config.name, 
                branch_name
            )
            
            if protection_info.get('enabled'):
                protection_key = f"protection:{repo_config.full_name}:{branch_name}"
                
                if self.change_detector.has_changed(protection_key, protection_info):
                    logger.debug(f"Branch protection updated for '{branch_name}' in {repo_config.full_name}")
                    result.items_updated += 1
                    result.items_synced += 1
                    
                    self.change_detector.mark_synced(protection_key, protection_info)
            
        except Exception as e:
            logger.error(f"Failed to sync branch protection for {branch_name}: {e}")
            result.add_error(f"Branch protection sync failed: {e}")
        
        return result
    
    def _analyze_merge_commit(self, repo_config: RepositoryConfig, commit: Commit) -> Optional[Dict[str, Any]]:
        """Analyze a merge commit to extract merge event information."""
        try:
            # Get detailed commit information
            commit_details = self.github_client.get_commit_details(
                repo_config.owner, 
                repo_config.name, 
                commit.sha
            )
            
            merge_event = {
                'sha': commit.sha,
                'message': commit.message,
                'author': commit.author,
                'committed_at': commit.committed_at,
                'parents': commit.parents,
                'merge_type': 'merge_commit',
                'files_changed': len(commit_details.get('files', [])),
                'additions': commit_details.get('stats', {}).get('additions', 0),
                'deletions': commit_details.get('stats', {}).get('deletions', 0),
                'total_changes': commit_details.get('stats', {}).get('total', 0)
            }
            
            # Try to determine source branch from commit message
            if 'merge pull request' in commit.message.lower():
                merge_event['merge_type'] = 'pull_request_merge'
                # Extract PR number if possible
                import re
                pr_match = re.search(r'#(\d+)', commit.message)
                if pr_match:
                    merge_event['pull_request_number'] = int(pr_match.group(1))
            
            return merge_event
            
        except Exception as e:
            logger.error(f"Failed to analyze merge commit {commit.sha}: {e}")
            return None
    
    def _sync_commit_relationships(self, repo_config: RepositoryConfig, commit: Commit) -> SyncResult:
        """Synchronize commit parent-child relationships."""
        result = SyncResult(success=True)
        
        try:
            # Store commit relationships for graph analysis
            for parent_sha in commit.parents:
                relationship_key = f"relationship:{repo_config.full_name}:{parent_sha}:{commit.sha}"
                
                relationship_data = {
                    'parent': parent_sha,
                    'child': commit.sha,
                    'branch': commit.branch,
                    'timestamp': commit.committed_at
                }
                
                if self.change_detector.has_changed(relationship_key, relationship_data):
                    logger.debug(f"Commit relationship updated: {parent_sha[:8]} -> {commit.sha[:8]}")
                    result.items_updated += 1
                    result.items_synced += 1
                    
                    self.change_detector.mark_synced(relationship_key, relationship_data)
            
        except Exception as e:
            logger.error(f"Failed to sync commit relationships for {commit.sha}: {e}")
            result.add_error(f"Commit relationship sync failed: {e}")
        
        return result
    
    def _process_merge_events(self, repo_config: RepositoryConfig, branch: str, 
                            merge_events: List[Dict[str, Any]]) -> SyncResult:
        """Process and store merge events for tracking project evolution."""
        result = SyncResult(success=True)
        
        try:
            for merge_event in merge_events:
                merge_key = f"merge:{repo_config.full_name}:{branch}:{merge_event['sha']}"
                
                if self.change_detector.has_changed(merge_key, merge_event):
                    logger.info(f"Merge event detected in {repo_config.full_name}:{branch}: {merge_event['merge_type']}")
                    result.items_updated += 1
                    result.items_synced += 1
                    
                    # Track merge impact on project state
                    if merge_event.get('pull_request_number'):
                        # Link merge event to PR for better tracking
                        pr_link_result = self._link_merge_to_pr(repo_config, merge_event)
                        result = result.merge(pr_link_result)
                    
                    self.change_detector.mark_synced(merge_key, merge_event)
            
        except Exception as e:
            logger.error(f"Failed to process merge events for {repo_config.full_name}:{branch}: {e}")
            result.add_error(f"Merge event processing failed: {e}")
        
        return result
    
    def _link_merge_to_pr(self, repo_config: RepositoryConfig, merge_event: Dict[str, Any]) -> SyncResult:
        """Link merge events to their corresponding pull requests."""
        result = SyncResult(success=True)
        
        try:
            pr_number = merge_event.get('pull_request_number')
            if pr_number:
                link_key = f"merge_pr_link:{repo_config.full_name}:{pr_number}:{merge_event['sha']}"
                
                link_data = {
                    'pr_number': pr_number,
                    'merge_sha': merge_event['sha'],
                    'merge_timestamp': merge_event['committed_at'],
                    'files_changed': merge_event['files_changed'],
                    'total_changes': merge_event['total_changes']
                }
                
                if self.change_detector.has_changed(link_key, link_data):
                    logger.debug(f"Linked merge {merge_event['sha'][:8]} to PR #{pr_number}")
                    result.items_updated += 1
                    result.items_synced += 1
                    
                    self.change_detector.mark_synced(link_key, link_data)
            
        except Exception as e:
            logger.error(f"Failed to link merge to PR: {e}")
            result.add_error(f"Merge-PR linking failed: {e}")
        
        return result
    
    def sync_all_repositories(self) -> Dict[str, SyncResult]:
        """
        Synchronize all configured repositories.
        
        Returns:
            Dictionary mapping repository names to sync results
        """
        results = {}
        
        if not self.sync_config.repositories:
            logger.warning("No repositories configured for synchronization")
            return results
        
        # Submit sync tasks to thread pool
        future_to_repo = {}
        for repo_config in self.sync_config.repositories:
            future = self.executor.submit(self.sync_repository, repo_config)
            future_to_repo[future] = repo_config.full_name
        
        # Collect results
        for future in as_completed(future_to_repo):
            repo_name = future_to_repo[future]
            try:
                result = future.result()
                results[repo_name] = result
            except Exception as e:
                logger.error(f"Sync task failed for {repo_name}: {e}")
                results[repo_name] = SyncResult(success=False, errors=[str(e)])
        
        return results
    
    def resolve_conflicts(self, conflicts: List[DataConflict]) -> ConflictResolution:
        """
        Resolve data synchronization conflicts.
        
        Args:
            conflicts: List of conflicts to resolve
            
        Returns:
            Conflict resolution result
        """
        resolution = ConflictResolution(
            conflicts_remaining=len(conflicts),
            resolution_strategy=self.conflict_resolver.strategy.value
        )
        
        for conflict in conflicts:
            try:
                resolved_data = self.conflict_resolver.resolve_conflict(conflict)
                
                if conflict.resolved:
                    resolution.add_resolution(conflict)
                    resolution.conflicts_remaining -= 1
                
            except Exception as e:
                logger.error(f"Failed to resolve conflict for {conflict.entity_type}:{conflict.entity_id}: {e}")
                resolution.add_error(f"Conflict resolution failed: {e}")
        
        return resolution
    
    def get_sync_status(self, repository_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get synchronization status for repositories.
        
        Args:
            repository_name: Optional specific repository name
            
        Returns:
            Synchronization status information
        """
        if repository_name:
            sync_state = self.sync_states.get(repository_name)
            if sync_state:
                return {
                    'repository': repository_name,
                    'status': sync_state.to_dict(),
                    'pending_conflicts': len(self.conflict_resolver.pending_conflicts)
                }
            else:
                return {'repository': repository_name, 'status': 'not_synced'}
        else:
            return {
                'repositories': {name: state.to_dict() for name, state in self.sync_states.items()},
                'total_pending_conflicts': len(self.conflict_resolver.pending_conflicts),
                'active_syncs': sum(1 for state in self.sync_states.values() if state.sync_in_progress)
            }
    
    def cleanup(self):
        """Clean up resources."""
        self.executor.shutdown(wait=True)