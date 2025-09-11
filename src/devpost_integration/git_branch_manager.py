#!/usr/bin/env python3
"""
Git Branch Manager - Branch management and switching

Extracted from git_integration.py for RM-DDD compliance.
Single responsibility: Branch management and switching operations.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from .git_operations import GitOperations

logger = logging.getLogger(__name__)


class GitBranchManager:
    """Manages git branches and switching operations"""
    
    def __init__(self, git_operations: GitOperations):
        """Initialize branch manager"""
        self.git_operations = git_operations
        self.current_branch = None
        self.available_branches = []
        self.branch_history = []
        
        # Branch management configuration
        self.auto_create_branch = True
        self.auto_switch_branch = True
        self.branch_prefix = "devpost-"
        
        # Statistics
        self.stats = {
            'branches_created': 0,
            'branches_switched': 0,
            'branches_deleted': 0,
            'merge_operations': 0,
            'last_operation': None
        }
        
        # Initialize current branch
        self._update_current_branch()
    
    def create_branch(self, branch_name: str, from_branch: Optional[str] = None) -> bool:
        """Create a new branch"""
        try:
            # Prepare branch name
            if not branch_name.startswith(self.branch_prefix):
                branch_name = f"{self.branch_prefix}{branch_name}"
            
            # Check if branch already exists
            if branch_name in self.available_branches:
                logger.warning(f"Branch {branch_name} already exists")
                return True
            
            # Create branch command
            if from_branch:
                success, stdout, stderr = self.git_operations.execute_git_command([
                    'checkout', '-b', branch_name, from_branch
                ])
            else:
                success, stdout, stderr = self.git_operations.execute_git_command([
                    'checkout', '-b', branch_name
                ])
            
            if success:
                self.stats['branches_created'] += 1
                self.stats['last_operation'] = f"created branch {branch_name}"
                self._update_available_branches()
                self._update_current_branch()
                logger.info(f"Created branch: {branch_name}")
                return True
            else:
                logger.error(f"Failed to create branch {branch_name}: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating branch {branch_name}: {e}")
            return False
    
    def switch_branch(self, branch_name: str) -> bool:
        """Switch to a branch"""
        try:
            # Check if branch exists
            if branch_name not in self.available_branches:
                if self.auto_create_branch:
                    logger.info(f"Branch {branch_name} not found, creating it")
                    return self.create_branch(branch_name)
                else:
                    logger.error(f"Branch {branch_name} does not exist")
                    return False
            
            # Switch to branch
            success, stdout, stderr = self.git_operations.execute_git_command([
                'checkout', branch_name
            ])
            
            if success:
                self.stats['branches_switched'] += 1
                self.stats['last_operation'] = f"switched to branch {branch_name}"
                self._update_current_branch()
                logger.info(f"Switched to branch: {branch_name}")
                return True
            else:
                logger.error(f"Failed to switch to branch {branch_name}: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error switching to branch {branch_name}: {e}")
            return False
    
    def delete_branch(self, branch_name: str, force: bool = False) -> bool:
        """Delete a branch"""
        try:
            # Check if branch exists
            if branch_name not in self.available_branches:
                logger.warning(f"Branch {branch_name} does not exist")
                return True
            
            # Check if trying to delete current branch
            if branch_name == self.current_branch:
                logger.error("Cannot delete current branch")
                return False
            
            # Delete branch
            delete_cmd = ['branch', '-D' if force else '-d', branch_name]
            success, stdout, stderr = self.git_operations.execute_git_command(delete_cmd)
            
            if success:
                self.stats['branches_deleted'] += 1
                self.stats['last_operation'] = f"deleted branch {branch_name}"
                self._update_available_branches()
                logger.info(f"Deleted branch: {branch_name}")
                return True
            else:
                logger.error(f"Failed to delete branch {branch_name}: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting branch {branch_name}: {e}")
            return False
    
    def merge_branch(self, source_branch: str, target_branch: Optional[str] = None) -> bool:
        """Merge a branch into current or target branch"""
        try:
            target = target_branch or self.current_branch
            if not target:
                logger.error("No target branch specified")
                return False
            
            # Switch to target branch if needed
            if target != self.current_branch:
                if not self.switch_branch(target):
                    return False
            
            # Merge source branch
            success, stdout, stderr = self.git_operations.execute_git_command([
                'merge', source_branch
            ])
            
            if success:
                self.stats['merge_operations'] += 1
                self.stats['last_operation'] = f"merged {source_branch} into {target}"
                logger.info(f"Merged {source_branch} into {target}")
                return True
            else:
                logger.error(f"Failed to merge {source_branch}: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error merging branch {source_branch}: {e}")
            return False
    
    def get_branch_info(self, branch_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a branch"""
        try:
            branch = branch_name or self.current_branch
            if not branch:
                return {'error': 'No branch specified'}
            
            # Get branch details
            success, stdout, stderr = self.git_operations.execute_git_command([
                'show-branch', branch
            ])
            
            if not success:
                return {'error': stderr}
            
            # Get last commit
            success, commit_info, stderr = self.git_operations.execute_git_command([
                'log', '-1', '--pretty=format:%H|%an|%ae|%ad|%s', branch
            ])
            
            commit_data = {}
            if success and commit_info:
                parts = commit_info.strip().split('|', 4)
                if len(parts) >= 5:
                    commit_data = {
                        'hash': parts[0],
                        'author_name': parts[1],
                        'author_email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    }
            
            return {
                'branch_name': branch,
                'is_current': branch == self.current_branch,
                'exists': branch in self.available_branches,
                'last_commit': commit_data,
                'branch_info': stdout
            }
            
        except Exception as e:
            logger.error(f"Error getting branch info: {e}")
            return {'error': str(e)}
    
    def list_branches(self, include_remote: bool = False) -> List[Dict[str, Any]]:
        """List all branches"""
        try:
            # Get local branches
            success, stdout, stderr = self.git_operations.execute_git_command([
                'branch', '--list'
            ])
            
            branches = []
            if success:
                for line in stdout.strip().split('\n'):
                    if line.strip():
                        branch_name = line.strip().lstrip('* ')
                        is_current = line.startswith('*')
                        branch_info = self.get_branch_info(branch_name)
                        branch_info['is_current'] = is_current
                        branches.append(branch_info)
            
            # Get remote branches if requested
            if include_remote:
                success, stdout, stderr = self.git_operations.execute_git_command([
                    'branch', '-r', '--list'
                ])
                
                if success:
                    for line in stdout.strip().split('\n'):
                        if line.strip() and not line.strip().startswith('origin/HEAD'):
                            branch_name = line.strip().replace('origin/', '')
                            if not any(b['branch_name'] == branch_name for b in branches):
                                branches.append({
                                    'branch_name': branch_name,
                                    'is_current': False,
                                    'is_remote': True,
                                    'exists': True
                                })
            
            return branches
            
        except Exception as e:
            logger.error(f"Error listing branches: {e}")
            return []
    
    def get_current_branch(self) -> Optional[str]:
        """Get current branch name"""
        return self.current_branch
    
    def get_available_branches(self) -> List[str]:
        """Get list of available branches"""
        return self.available_branches.copy()
    
    def _update_current_branch(self) -> None:
        """Update current branch information"""
        try:
            success, stdout, stderr = self.git_operations.execute_git_command([
                'rev-parse', '--abbrev-ref', 'HEAD'
            ])
            
            if success and stdout.strip():
                self.current_branch = stdout.strip()
            else:
                self.current_branch = None
                
        except Exception as e:
            logger.error(f"Error updating current branch: {e}")
            self.current_branch = None
    
    def _update_available_branches(self) -> None:
        """Update list of available branches"""
        try:
            success, stdout, stderr = self.git_operations.execute_git_command([
                'branch', '--list'
            ])
            
            if success:
                self.available_branches = [
                    line.strip().lstrip('* ') 
                    for line in stdout.strip().split('\n') 
                    if line.strip()
                ]
            else:
                self.available_branches = []
                
        except Exception as e:
            logger.error(f"Error updating available branches: {e}")
            self.available_branches = []
    
    def get_branch_stats(self) -> Dict[str, Any]:
        """Get branch management statistics"""
        return {
            'branch_stats': self.stats.copy(),
            'current_branch': self.current_branch,
            'available_branches': self.available_branches,
            'total_branches': len(self.available_branches),
            'last_operation': self.stats['last_operation']
        }
    
    def is_healthy(self) -> bool:
        """Check if branch manager is healthy"""
        try:
            # Check if git operations are healthy
            if not self.git_operations.is_healthy():
                return False
            
            # Check if we can get current branch
            current_branch = self.get_current_branch()
            if not current_branch:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators"""
        try:
            return {
                'branch_manager_healthy': self.is_healthy(),
                'git_operations_healthy': self.git_operations.is_healthy(),
                'current_branch': self.current_branch,
                'available_branches_count': len(self.available_branches),
                'branch_stats': self.stats,
                'last_operation': self.stats['last_operation']
            }
        except Exception as e:
            return {
                'branch_manager_healthy': False,
                'error': str(e)
            }
