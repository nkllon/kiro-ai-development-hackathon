from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


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
    