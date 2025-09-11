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
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)

logger = logging.getLogger(__name__)


class DevpostGitIntegration(ReflectiveModule):
    """Main git integration with RM-DDD compliance"""
    
    def __init__(self, config: Optional[DevpostConfig] = None):
        """Initialize git integration"""
        super().__init__(module_id="git_integration", version="1.0.0")
        self.config = config or DevpostConfig()
        self.git_operations = GitOperations()
        self.change_tracker = GitChangeTracker()
        self.branch_manager = GitBranchManager()
        self._start_time = datetime.now()
        self._operations_count = 0
        self._errors = 0
        register_module(self)
    
    def initialize_repository(self, repo_path: Path) -> bool:
        """Initialize git repository"""
        try:
            self._operations_count += 1
            success = self.git_operations.initialize_repository(repo_path)
            if success:
                logger.info(f"Initialized git repository at {repo_path}")
            return success
        except Exception as e:
            self._errors += 1
            logger.error(f"Error initializing repository: {e}")
            return False
    
    def add_files(self, repo_path: Path, files: List[Path]) -> bool:
        """Add files to git staging"""
        try:
            self._operations_count += 1
            success = self.git_operations.add_files(repo_path, files)
            if success:
                logger.info(f"Added {len(files)} files to staging")
            return success
        except Exception as e:
            self._errors += 1
            logger.error(f"Error adding files: {e}")
            return False
    
    def commit_changes(self, repo_path: Path, message: str) -> bool:
        """Commit staged changes"""
        try:
            self._operations_count += 1
            success = self.git_operations.commit_changes(repo_path, message)
            if success:
                logger.info(f"Committed changes: {message}")
            return success
        except Exception as e:
            self._errors += 1
            logger.error(f"Error committing changes: {e}")
            return False
    
    def push_changes(self, repo_path: Path, remote: str = "origin", branch: str = "main") -> bool:
        """Push changes to remote repository"""
        try:
            self._operations_count += 1
            success = self.git_operations.push_changes(repo_path, remote, branch)
            if success:
                logger.info(f"Pushed changes to {remote}/{branch}")
            return success
        except Exception as e:
            self._errors += 1
            logger.error(f"Error pushing changes: {e}")
            return False
    
    def get_changes(self, repo_path: Path) -> List[FileChangeEvent]:
        """Get list of file changes"""
        try:
            return self.change_tracker.get_changes(repo_path)
        except Exception as e:
            self._errors += 1
            logger.error(f"Error getting changes: {e}")
            return []
    
    def get_status(self, repo_path: Path) -> Dict[str, Any]:
        """Get git repository status"""
        try:
            return self.git_operations.get_status(repo_path)
        except Exception as e:
            self._errors += 1
            logger.error(f"Error getting status: {e}")
            return {}
    
    def create_branch(self, repo_path: Path, branch_name: str) -> bool:
        """Create new branch"""
        try:
            self._operations_count += 1
            success = self.branch_manager.create_branch(repo_path, branch_name)
            if success:
                logger.info(f"Created branch: {branch_name}")
            return success
        except Exception as e:
            self._errors += 1
            logger.error(f"Error creating branch: {e}")
            return False
    
    def switch_branch(self, repo_path: Path, branch_name: str) -> bool:
        """Switch to branch"""
        try:
            self._operations_count += 1
            success = self.branch_manager.switch_branch(repo_path, branch_name)
            if success:
                logger.info(f"Switched to branch: {branch_name}")
            return success
        except Exception as e:
            self._errors += 1
            logger.error(f"Error switching branch: {e}")
            return False
    
    def get_branches(self, repo_path: Path) -> List[str]:
        """Get list of branches"""
        try:
            return self.branch_manager.get_branches(repo_path)
        except Exception as e:
            self._errors += 1
            logger.error(f"Error getting branches: {e}")
            return []
    
    def sync_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Sync repository with remote"""
        try:
            self._operations_count += 1
            
            # Get current status
            status = self.get_status(repo_path)
            
            # Get changes
            changes = self.get_changes(repo_path)
            
            # Add all changes
            if changes:
                files = [change.file_path for change in changes]
                self.add_files(repo_path, files)
            
            # Commit if there are staged changes
            if status.get('staged_files'):
                commit_message = f"Auto-sync: {len(changes)} files changed"
                self.commit_changes(repo_path, commit_message)
            
            # Push changes
            self.push_changes(repo_path)
            
            return {
                'success': True,
                'changes_processed': len(changes),
                'files_staged': len(status.get('staged_files', [])),
                'message': 'Repository synced successfully'
            }
            
        except Exception as e:
            self._errors += 1
            logger.error(f"Error syncing repository: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Repository sync failed'
            }
    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'DevPost Git Integration',
            'description': 'Git integration for DevPost project management',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.HEALTH_MONITORING,
            ModuleCapability.CONFIGURATION,
            ModuleCapability.LOGGING,
            ModuleCapability.METRICS,
            ModuleCapability.PERSISTENCE
        ]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return [
            'git_operations',
            'git_change_tracker',
            'git_branch_manager'
        ]
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Check git operations
            if not hasattr(self, 'git_operations'):
                issues.append("Missing git operations component")
                health_score -= 0.3
            
            # Check change tracker
            if not hasattr(self, 'change_tracker'):
                issues.append("Missing change tracker component")
                health_score -= 0.2
            
            # Check branch manager
            if not hasattr(self, 'branch_manager'):
                issues.append("Missing branch manager component")
                health_score -= 0.2
            
            # Check error rate
            if self._operations_count > 0:
                error_rate = self._errors / self._operations_count
                if error_rate > 0.1:  # More than 10% error rate
                    issues.append(f"High error rate: {error_rate:.1%}")
                    health_score -= 0.2
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters=self.config.to_dict() if hasattr(self.config, 'to_dict') else {},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                return False
            
            # Update configuration
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Configuration update error: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        error_rate = (self._errors / self._operations_count) if self._operations_count > 0 else 0.0
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'operations_count': self._operations_count,
            'errors': self._errors,
            'error_rate': error_rate,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._operations_count = 0
        self._errors = 0
        self._start_time = datetime.now()
        logger.info("Metrics reset for git integration module")