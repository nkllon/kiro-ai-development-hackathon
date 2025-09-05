"""
Git session management for task execution.
"""
import subprocess
from datetime import datetime
from typing import Optional
import logging

class GitSession:
    """Manages Git operations for task execution sessions."""
    
    def __init__(self, base_branch: str = "main"):
        self.base_branch = base_branch
        self.branch_name: Optional[str] = None
        self.changes_made = False
        self.logger = logging.getLogger(__name__)
    
    def create_session_branch(self) -> bool:
        """Create a new branch for the execution session."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.branch_name = f"task_execution_{timestamp}"
        
        try:
            # Create and checkout new branch
            subprocess.run(
                ["git", "checkout", "-b", self.branch_name],
                check=True, capture_output=True
            )
            self.logger.info(f"Created session branch: {self.branch_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create session branch: {e}")
            return False
    
    def commit_changes(self, message: str) -> bool:
        """Commit current changes."""
        try:
            # Add all changes
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            
            # Commit changes
            subprocess.run(
                ["git", "commit", "-m", message],
                check=True, capture_output=True
            )
            
            self.changes_made = True
            self.logger.info(f"Committed changes: {message}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to commit changes: {e}")
            return False
    
    def push_branch(self) -> bool:
        """Push the session branch to remote."""
        if not self.branch_name:
            return False
        
        try:
            subprocess.run(
                ["git", "push", "-u", "origin", self.branch_name],
                check=True, capture_output=True
            )
            self.logger.info(f"Pushed branch: {self.branch_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to push branch: {e}")
            return False
    
    def merge_to_base(self) -> bool:
        """Merge session branch back to base branch."""
        if not self.branch_name:
            return False
        
        try:
            # Switch to base branch
            subprocess.run(
                ["git", "checkout", self.base_branch],
                check=True, capture_output=True
            )
            
            # Merge session branch
            subprocess.run(
                ["git", "merge", self.branch_name],
                check=True, capture_output=True
            )
            
            self.logger.info(f"Merged {self.branch_name} to {self.base_branch}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to merge branch: {e}")
            return False
    
    def cleanup_branch(self) -> bool:
        """Delete the session branch."""
        if not self.branch_name:
            return False
        
        try:
            # Delete local branch
            subprocess.run(
                ["git", "branch", "-d", self.branch_name],
                check=True, capture_output=True
            )
            
            # Delete remote branch
            subprocess.run(
                ["git", "push", "origin", "--delete", self.branch_name],
                check=True, capture_output=True
            )
            
            self.logger.info(f"Cleaned up branch: {self.branch_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to cleanup branch: {e}")
            return False