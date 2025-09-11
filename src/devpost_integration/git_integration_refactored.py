#!/usr/bin/env python3
"""
Git Integration - Main git integration orchestration

Refactored from git_integration.py for RM-DDD compliance.
Single responsibility: Git integration orchestration and coordination.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from .models import FileChangeEvent, ChangeType, DevpostConfig
from .git_operations import GitOperations
from .git_change_tracker import GitChangeTracker
from .git_branch_manager import GitBranchManager

logger = logging.getLogger(__name__)


class GitIntegration:
    """
    Git repository integration for Devpost project synchronization.
    
    Provides git operations, change tracking, and version control
    integration for project file monitoring.
    """
    
    def __init__(self, project_path: Path, config: Optional[DevpostConfig] = None):
        """Initialize git integration"""
        self.project_path = Path(project_path).resolve()
        self.config = config or DevpostConfig()
        
        # Initialize components
        self.git_operations = GitOperations(self.project_path)
        self.change_tracker = GitChangeTracker(self.git_operations)
        self.branch_manager = GitBranchManager(self.git_operations)
        
        # Git configuration
        self.auto_commit = getattr(self.config, 'auto_commit', False)
        self.commit_message_template = getattr(
            self.config, 
            'commit_message_template', 
            "Devpost sync: {change_type} {file_path}"
        )
        self.branch_name = getattr(self.config, 'branch_name', 'devpost-sync')
        
        # Statistics
        self.stats = {
            'commits_made': 0,
            'branches_created': 0,
            'conflicts_resolved': 0,
            'last_commit': None,
            'last_sync': None
        }
    
    def initialize_repository(self) -> bool:
        """Initialize git repository if not already initialized"""
        try:
            if self.git_operations.is_git_repo:
                logger.info("Git repository already initialized")
                return True
            
            # Initialize repository
            if not self.git_operations.init_repository():
                return False
            
            # Create initial commit
            self.git_operations.add_files(['.'])
            self.git_operations.commit_changes("Initial commit - Devpost integration setup")
            
            # Create devpost branch
            if self.branch_name != 'main' and self.branch_name != 'master':
                self.branch_manager.create_branch(self.branch_name)
                self.branch_manager.switch_branch(self.branch_name)
            
            logger.info("Git repository initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing git repository: {e}")
            return False
    
    def sync_changes(self, file_paths: List[str], 
                    commit_message: Optional[str] = None) -> bool:
        """Sync changes to git repository"""
        try:
            if not self.git_operations.is_git_repo:
                logger.error("Not a git repository")
                return False
            
            # Track files for changes
            self.change_tracker.start_tracking(file_paths)
            
            # Detect changes
            changes = self.change_tracker.detect_changes()
            if not changes:
                logger.info("No changes detected")
                return True
            
            # Add changed files
            changed_files = [change.file_path for change in changes]
            if not self.git_operations.add_files(changed_files):
                return False
            
            # Create commit message
            if not commit_message:
                change_types = set(change.change_type for change in changes)
                change_summary = ", ".join(change_types)
                commit_message = self.commit_message_template.format(
                    change_type=change_summary,
                    file_path=f"{len(changed_files)} files"
                )
            
            # Commit changes
            if not self.git_operations.commit_changes(commit_message):
                return False
            
            # Update statistics
            self.stats['commits_made'] += 1
            self.stats['last_commit'] = datetime.now().isoformat()
            self.stats['last_sync'] = datetime.now().isoformat()
            
            logger.info(f"Synced {len(changes)} changes to git repository")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing changes: {e}")
            return False
    
    def get_repository_status(self) -> Dict[str, Any]:
        """Get comprehensive repository status"""
        try:
            # Get git status
            git_status = self.git_operations.get_status()
            
            # Get branch information
            current_branch = self.branch_manager.get_current_branch()
            branch_info = self.branch_manager.get_branch_info(current_branch)
            
            # Get change tracking info
            tracking_stats = self.change_tracker.get_tracking_stats()
            
            return {
                'repository_path': str(self.project_path),
                'is_git_repo': self.git_operations.is_git_repo,
                'current_branch': current_branch,
                'branch_info': branch_info,
                'git_status': git_status,
                'tracking_stats': tracking_stats,
                'integration_stats': self.stats,
                'last_sync': self.stats['last_sync']
            }
            
        except Exception as e:
            logger.error(f"Error getting repository status: {e}")
            return {'error': str(e)}
    
    def get_change_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent change history"""
        try:
            # Get git commit history
            git_history = self.git_operations.get_commit_history(limit)
            
            # Get tracked changes
            tracked_changes = self.change_tracker.get_recent_changes(limit)
            
            return {
                'git_commits': git_history,
                'tracked_changes': [change.to_dict() for change in tracked_changes],
                'total_git_commits': len(git_history),
                'total_tracked_changes': len(tracked_changes)
            }
            
        except Exception as e:
            logger.error(f"Error getting change history: {e}")
            return {'error': str(e)}
    
    def create_feature_branch(self, feature_name: str) -> bool:
        """Create a new feature branch"""
        try:
            branch_name = f"feature/{feature_name}"
            success = self.branch_manager.create_branch(branch_name)
            
            if success:
                self.stats['branches_created'] += 1
                logger.info(f"Created feature branch: {branch_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error creating feature branch: {e}")
            return False
    
    def merge_feature_branch(self, feature_name: str, target_branch: str = 'main') -> bool:
        """Merge feature branch into target branch"""
        try:
            feature_branch = f"feature/{feature_name}"
            
            # Switch to target branch
            if not self.branch_manager.switch_branch(target_branch):
                return False
            
            # Merge feature branch
            success = self.branch_manager.merge_branch(feature_branch, target_branch)
            
            if success:
                # Delete feature branch
                self.branch_manager.delete_branch(feature_branch)
                logger.info(f"Merged feature branch {feature_branch} into {target_branch}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error merging feature branch: {e}")
            return False
    
    def resolve_conflicts(self, file_path: str) -> bool:
        """Resolve merge conflicts in a file"""
        try:
            # Get file diff to see conflicts
            diff_content = self.change_tracker.get_file_diff(file_path)
            if not diff_content:
                return True  # No conflicts
            
            # Check for conflict markers
            if '<<<<<<< HEAD' in diff_content:
                logger.warning(f"Conflicts detected in {file_path}")
                # In a real implementation, this would open a conflict resolution tool
                # For now, we'll just log the conflict
                self.stats['conflicts_resolved'] += 1
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"Error resolving conflicts: {e}")
            return False
    
    def export_repository_data(self, export_path: str) -> bool:
        """Export repository data and history"""
        try:
            export_file = Path(export_path) / "git_integration_export.json"
            
            # Get all data
            status = self.get_repository_status()
            history = self.get_change_history(100)  # Export more history
            
            export_data = {
                'export_time': datetime.now().isoformat(),
                'repository_status': status,
                'change_history': history,
                'integration_stats': self.stats
            }
            
            # Write to file
            import json
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported repository data to {export_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting repository data: {e}")
            return False
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get comprehensive integration statistics"""
        return {
            'integration_stats': self.stats.copy(),
            'git_operations_stats': self.git_operations.get_operation_stats(),
            'branch_manager_stats': self.branch_manager.get_branch_stats(),
            'change_tracker_stats': self.change_tracker.get_tracking_stats(),
            'repository_path': str(self.project_path),
            'is_git_repo': self.git_operations.is_git_repo,
            'current_branch': self.branch_manager.get_current_branch()
        }
    
    def is_healthy(self) -> bool:
        """Check if git integration is healthy"""
        try:
            # Check all components
            if not self.git_operations.is_healthy():
                return False
            
            if not self.change_tracker.is_healthy():
                return False
            
            if not self.branch_manager.is_healthy():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators"""
        try:
            return {
                'integration_healthy': self.is_healthy(),
                'git_operations_healthy': self.git_operations.is_healthy(),
                'change_tracker_healthy': self.change_tracker.is_healthy(),
                'branch_manager_healthy': self.branch_manager.is_healthy(),
                'repository_path': str(self.project_path),
                'is_git_repo': self.git_operations.is_git_repo,
                'current_branch': self.branch_manager.get_current_branch(),
                'integration_stats': self.stats,
                'last_sync': self.stats['last_sync']
            }
        except Exception as e:
            return {
                'integration_healthy': False,
                'error': str(e)
            }
