"""
Devpost Sync Manager - Minimal Implementation

Handles synchronization between local project and Devpost submission.
"""

from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    changes_made: List[str]
    error: Optional[str] = None


class DevpostSyncManager:
    """Manages synchronization with Devpost."""
    
    def __init__(self):
        self.config_path = Path('.devpost/config.json')
    
    def get_pending_changes(self) -> List[str]:
        """Get list of pending changes to sync."""
        # Minimal implementation - check for common changes
        changes = []
        
        if Path('README.md').exists():
            changes.append("README.md - Project description")
        
        if Path('package.json').exists():
            changes.append("package.json - Project metadata")
        
        # Check for media files
        for pattern in ['*.png', '*.jpg', '*.gif', '*.mp4']:
            if list(Path('.').glob(pattern)):
                changes.append(f"Media files - {pattern}")
        
        return changes
    
    def sync_project(self, force: bool = False) -> SyncResult:
        """Sync project with Devpost."""
        try:
            changes = self.get_pending_changes()
            
            if not changes and not force:
                return SyncResult(success=True, changes_made=[])
            
            # Simulate sync operation
            synced_changes = []
            for change in changes:
                # In real implementation, this would call Devpost API
                synced_changes.append(f"Synced: {change}")
            
            return SyncResult(success=True, changes_made=synced_changes)
            
        except Exception as e:
            return SyncResult(success=False, changes_made=[], error=str(e))