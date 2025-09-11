#!/usr/bin/env python3
"""
Git Operations - Core git operations and commands

Extracted from git_integration.py for RM-DDD compliance.
Single responsibility: Core git operations and command execution.
"""

import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json

logger = logging.getLogger(__name__)


class GitOperations:
    """Core git operations and command execution"""
    
    def __init__(self, project_path: Path):
        """Initialize git operations"""
        self.project_path = Path(project_path).resolve()
        self.is_git_repo = self._check_git_repository()
        
        # Git command configuration
        self.git_timeout = 30
        self.max_retries = 3
        
        # Statistics
        self.stats = {
            'commands_executed': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'last_command': None,
            'last_error': None
        }
    
    def execute_git_command(self, command: List[str], 
                           capture_output: bool = True, 
                           timeout: Optional[int] = None) -> Tuple[bool, str, str]:
        """Execute a git command and return results"""
        try:
            self.stats['commands_executed'] += 1
            self.stats['last_command'] = ' '.join(command)
            
            # Add git prefix if not present
            if not command[0].startswith('git'):
                command = ['git'] + command
            
            # Set working directory
            cwd = self.project_path
            
            # Execute command
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=timeout or self.git_timeout
            )
            
            if result.returncode == 0:
                self.stats['successful_commands'] += 1
                self.stats['last_error'] = None
                return True, result.stdout, result.stderr
            else:
                self.stats['failed_commands'] += 1
                self.stats['last_error'] = result.stderr
                return False, result.stdout, result.stderr
                
        except subprocess.TimeoutExpired:
            self.stats['failed_commands'] += 1
            self.stats['last_error'] = 'Command timeout'
            return False, '', 'Command timeout'
        except Exception as e:
            self.stats['failed_commands'] += 1
            self.stats['last_error'] = str(e)
            return False, '', str(e)
    
    def init_repository(self) -> bool:
        """Initialize git repository"""
        try:
            if self.is_git_repo:
                logger.info("Git repository already initialized")
                return True
            
            success, stdout, stderr = self.execute_git_command(['init'])
            
            if success:
                self.is_git_repo = True
                logger.info("Git repository initialized successfully")
                return True
            else:
                logger.error(f"Failed to initialize git repository: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing git repository: {e}")
            return False
    
    def add_files(self, files: List[str]) -> bool:
        """Add files to git staging area"""
        try:
            if not files:
                return True
            
            # Add files
            success, stdout, stderr = self.execute_git_command(['add'] + files)
            
            if success:
                logger.info(f"Added {len(files)} files to staging area")
                return True
            else:
                logger.error(f"Failed to add files: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding files: {e}")
            return False
    
    def commit_changes(self, message: str, author: Optional[str] = None) -> bool:
        """Commit staged changes"""
        try:
            # Check if there are changes to commit
            success, stdout, stderr = self.execute_git_command(['diff', '--cached', '--quiet'])
            if success:
                logger.info("No changes to commit")
                return True
            
            # Prepare commit command
            commit_cmd = ['commit', '-m', message]
            if author:
                commit_cmd.extend(['--author', author])
            
            success, stdout, stderr = self.execute_git_command(commit_cmd)
            
            if success:
                logger.info(f"Committed changes: {message}")
                return True
            else:
                logger.error(f"Failed to commit changes: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get git repository status"""
        try:
            # Get status
            success, stdout, stderr = self.execute_git_command(['status', '--porcelain'])
            if not success:
                return {'error': stderr}
            
            # Parse status
            status_lines = stdout.strip().split('\n') if stdout.strip() else []
            
            status = {
                'is_git_repo': self.is_git_repo,
                'has_changes': len(status_lines) > 0,
                'staged_files': [],
                'modified_files': [],
                'untracked_files': [],
                'deleted_files': [],
                'renamed_files': []
            }
            
            for line in status_lines:
                if len(line) >= 2:
                    status_code = line[:2]
                    file_path = line[3:]
                    
                    if status_code[0] == 'A':
                        status['staged_files'].append(file_path)
                    elif status_code[0] == 'M':
                        status['modified_files'].append(file_path)
                    elif status_code[0] == '?':
                        status['untracked_files'].append(file_path)
                    elif status_code[0] == 'D':
                        status['deleted_files'].append(file_path)
                    elif status_code[0] == 'R':
                        status['renamed_files'].append(file_path)
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting git status: {e}")
            return {'error': str(e)}
    
    def get_commit_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get commit history"""
        try:
            success, stdout, stderr = self.execute_git_command([
                'log', '--oneline', '--max-count', str(limit), '--pretty=format:%H|%an|%ae|%ad|%s'
            ])
            
            if not success:
                return []
            
            commits = []
            for line in stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 4)
                    if len(parts) >= 5:
                        commits.append({
                            'hash': parts[0],
                            'author_name': parts[1],
                            'author_email': parts[2],
                            'date': parts[3],
                            'message': parts[4]
                        })
            
            return commits
            
        except Exception as e:
            logger.error(f"Error getting commit history: {e}")
            return []
    
    def get_file_diff(self, file_path: str) -> str:
        """Get diff for a specific file"""
        try:
            success, stdout, stderr = self.execute_git_command(['diff', file_path])
            
            if success:
                return stdout
            else:
                return stderr
                
        except Exception as e:
            logger.error(f"Error getting file diff: {e}")
            return str(e)
    
    def reset_changes(self, file_path: Optional[str] = None) -> bool:
        """Reset changes for file or all files"""
        try:
            if file_path:
                success, stdout, stderr = self.execute_git_command(['checkout', '--', file_path])
            else:
                success, stdout, stderr = self.execute_git_command(['reset', '--hard', 'HEAD'])
            
            if success:
                logger.info(f"Reset changes for {file_path or 'all files'}")
                return True
            else:
                logger.error(f"Failed to reset changes: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error resetting changes: {e}")
            return False
    
    def stash_changes(self, message: str = "Stashed changes") -> bool:
        """Stash current changes"""
        try:
            success, stdout, stderr = self.execute_git_command(['stash', 'push', '-m', message])
            
            if success:
                logger.info("Changes stashed successfully")
                return True
            else:
                logger.error(f"Failed to stash changes: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error stashing changes: {e}")
            return False
    
    def pop_stash(self) -> bool:
        """Pop the most recent stash"""
        try:
            success, stdout, stderr = self.execute_git_command(['stash', 'pop'])
            
            if success:
                logger.info("Stash popped successfully")
                return True
            else:
                logger.error(f"Failed to pop stash: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error popping stash: {e}")
            return False
    
    def get_remote_url(self) -> Optional[str]:
        """Get remote repository URL"""
        try:
            success, stdout, stderr = self.execute_git_command(['config', '--get', 'remote.origin.url'])
            
            if success and stdout.strip():
                return stdout.strip()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting remote URL: {e}")
            return None
    
    def set_remote_url(self, url: str) -> bool:
        """Set remote repository URL"""
        try:
            success, stdout, stderr = self.execute_git_command(['remote', 'add', 'origin', url])
            
            if success:
                logger.info(f"Remote URL set to: {url}")
                return True
            else:
                # Try to update existing remote
                success, stdout, stderr = self.execute_git_command(['remote', 'set-url', 'origin', url])
                if success:
                    logger.info(f"Remote URL updated to: {url}")
                    return True
                else:
                    logger.error(f"Failed to set remote URL: {stderr}")
                    return False
                
        except Exception as e:
            logger.error(f"Error setting remote URL: {e}")
            return False
    
    def _check_git_repository(self) -> bool:
        """Check if project path is a git repository"""
        try:
            success, stdout, stderr = self.execute_git_command(['rev-parse', '--git-dir'])
            return success
        except Exception:
            return False
    
    def get_operation_stats(self) -> Dict[str, Any]:
        """Get git operation statistics"""
        return {
            'is_git_repo': self.is_git_repo,
            'project_path': str(self.project_path),
            'stats': self.stats.copy(),
            'remote_url': self.get_remote_url()
        }
    
    def is_healthy(self) -> bool:
        """Check if git operations are healthy"""
        try:
            # Test basic git command
            success, _, _ = self.execute_git_command(['--version'])
            return success and self.is_git_repo
        except Exception:
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators"""
        try:
            return {
                'operations_healthy': self.is_healthy(),
                'is_git_repo': self.is_git_repo,
                'project_path': str(self.project_path),
                'stats': self.stats,
                'remote_url': self.get_remote_url(),
                'last_command': self.stats['last_command'],
                'last_error': self.stats['last_error']
            }
        except Exception as e:
            return {
                'operations_healthy': False,
                'error': str(e)
            }
