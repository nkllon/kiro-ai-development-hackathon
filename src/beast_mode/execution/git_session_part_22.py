from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


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