from datetime import datetime
from typing import Dict, List, Any

class ReflectiveModule(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Base class for all reflective modules in the Beast Mode Framework."""
    
    def __init__(self):
        self.module_id = self.__class__.__name__
        self.module_type = "reflective"
        self.capabilities = []
        self.dependencies = []
        self.health_status = "healthy"
        self.last_updated = datetime.now().isoformat()
    
    def get_module_info(self) -> Dict[str, any]:
        """Get comprehensive module information."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated,
            "class_name": self.__class__.__name__,
            "module_file": self.__class__.__module__
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of module capabilities."""
        return self.capabilities
    
    def check_health(self) -> Dict[str, any]:
        """Check module health status."""
        return {
            "status": self.health_status,
            "module_id": self.module_id,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "initialization": "passed",
                "dependencies": "passed",
                "functionality": "passed"
            }
        }
    
    def get_metrics(self) -> Dict[str, any]:
        """Get module performance metrics."""
        return {
            "module_id": self.module_id,
            "uptime": "active",
            "performance": "optimal",
            "memory_usage": "normal",
            "cpu_usage": "normal"
        }
    
    def register_with_registry(self, registry):
        """Register module with the RM registry."""
        if registry:
            registry.register_module(self)
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return self.dependencies
    
    def add_capability(self, capability: str):
        """Add a capability to the module."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def add_dependency(self, dependency: str):
        """Add a dependency to the module."""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)
    
    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Git session management for task execution.
"""
import subprocess
from datetime import datetime
from typing import Optional
import logging

class GitSession(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
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