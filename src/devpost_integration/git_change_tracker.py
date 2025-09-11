#!/usr/bin/env python3
"""
Git Change Tracker - Change tracking and diff analysis

Extracted from git_integration.py for RM-DDD compliance.
Single responsibility: Change tracking and diff analysis.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

from .models import FileChangeEvent, ChangeType
from .git_operations import GitOperations

logger = logging.getLogger(__name__)


class GitChangeTracker:
    """Tracks file changes and provides diff analysis"""
    
    def __init__(self, git_operations: GitOperations):
        """Initialize change tracker"""
        self.git_operations = git_operations
        self.tracked_files: Set[str] = set()
        self.file_hashes: Dict[str, str] = {}
        self.change_history: List[FileChangeEvent] = []
        
        # Change detection configuration
        self.track_ignored_files = False
        self.track_binary_files = True
        self.max_history_size = 1000
        
        # Statistics
        self.stats = {
            'files_tracked': 0,
            'changes_detected': 0,
            'diffs_generated': 0,
            'last_scan_time': None
        }
    
    def start_tracking(self, file_paths: List[str]) -> bool:
        """Start tracking specified files"""
        try:
            for file_path in file_paths:
                self.tracked_files.add(file_path)
                self._update_file_hash(file_path)
            
            self.stats['files_tracked'] = len(self.tracked_files)
            logger.info(f"Started tracking {len(file_paths)} files")
            return True
            
        except Exception as e:
            logger.error(f"Error starting file tracking: {e}")
            return False
    
    def stop_tracking(self, file_paths: List[str]) -> bool:
        """Stop tracking specified files"""
        try:
            for file_path in file_paths:
                self.tracked_files.discard(file_path)
                self.file_hashes.pop(file_path, None)
            
            self.stats['files_tracked'] = len(self.tracked_files)
            logger.info(f"Stopped tracking {len(file_paths)} files")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping file tracking: {e}")
            return False
    
    def detect_changes(self) -> List[FileChangeEvent]:
        """Detect changes in tracked files"""
        try:
            changes = []
            current_time = datetime.now().isoformat()
            
            for file_path in self.tracked_files:
                file_path_obj = Path(file_path)
                
                # Check if file exists
                if not file_path_obj.exists():
                    # File was deleted
                    if file_path in self.file_hashes:
                        changes.append(FileChangeEvent(
                            file_path=file_path,
                            change_type=ChangeType.REMOVED,
                            content_type='file',
                            timestamp=current_time,
                            metadata={'previous_hash': self.file_hashes[file_path]}
                        ))
                        del self.file_hashes[file_path]
                else:
                    # File exists, check for changes
                    current_hash = self._calculate_file_hash(file_path_obj)
                    previous_hash = self.file_hashes.get(file_path)
                    
                    if previous_hash is None:
                        # New file
                        changes.append(FileChangeEvent(
                            file_path=file_path,
                            change_type=ChangeType.ADDED,
                            content_type='file',
                            timestamp=current_time,
                            metadata={'file_hash': current_hash}
                        ))
                    elif current_hash != previous_hash:
                        # Modified file
                        changes.append(FileChangeEvent(
                            file_path=file_path,
                            change_type=ChangeType.MODIFIED,
                            content_type='file',
                            timestamp=current_time,
                            metadata={
                                'previous_hash': previous_hash,
                                'current_hash': current_hash
                            }
                        ))
                    
                    # Update hash
                    self.file_hashes[file_path] = current_hash
            
            # Update statistics
            self.stats['changes_detected'] += len(changes)
            self.stats['last_scan_time'] = current_time
            
            # Add to history
            self.change_history.extend(changes)
            if len(self.change_history) > self.max_history_size:
                self.change_history = self.change_history[-self.max_history_size:]
            
            if changes:
                logger.info(f"Detected {len(changes)} changes in tracked files")
            
            return changes
            
        except Exception as e:
            logger.error(f"Error detecting changes: {e}")
            return []
    
    def get_file_diff(self, file_path: str) -> Optional[str]:
        """Get diff for a specific file"""
        try:
            if not self.git_operations.is_git_repo:
                return None
            
            diff_content = self.git_operations.get_file_diff(file_path)
            self.stats['diffs_generated'] += 1
            
            return diff_content
            
        except Exception as e:
            logger.error(f"Error getting file diff: {e}")
            return None
    
    def get_change_summary(self, file_path: str) -> Dict[str, Any]:
        """Get summary of changes for a file"""
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                return {
                    'file_path': file_path,
                    'status': 'deleted',
                    'exists': False,
                    'last_modified': None,
                    'size': 0
                }
            
            stat = file_path_obj.stat()
            return {
                'file_path': file_path,
                'status': 'exists',
                'exists': True,
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'size': stat.st_size,
                'is_tracked': file_path in self.tracked_files,
                'current_hash': self.file_hashes.get(file_path),
                'has_git_diff': bool(self.get_file_diff(file_path))
            }
            
        except Exception as e:
            logger.error(f"Error getting change summary: {e}")
            return {
                'file_path': file_path,
                'status': 'error',
                'error': str(e)
            }
    
    def get_recent_changes(self, limit: int = 10) -> List[FileChangeEvent]:
        """Get recent changes from history"""
        return self.change_history[-limit:] if self.change_history else []
    
    def get_changes_by_type(self, change_type: ChangeType) -> List[FileChangeEvent]:
        """Get changes filtered by type"""
        return [change for change in self.change_history if change.change_type == change_type]
    
    def get_changes_for_file(self, file_path: str) -> List[FileChangeEvent]:
        """Get all changes for a specific file"""
        return [change for change in self.change_history if change.file_path == file_path]
    
    def clear_history(self) -> None:
        """Clear change history"""
        self.change_history.clear()
        logger.info("Change history cleared")
    
    def export_changes(self, file_path: str) -> bool:
        """Export change history to file"""
        try:
            import json
            
            export_data = {
                'export_time': datetime.now().isoformat(),
                'total_changes': len(self.change_history),
                'tracked_files': list(self.tracked_files),
                'changes': [change.to_dict() for change in self.change_history]
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported {len(self.change_history)} changes to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting changes: {e}")
            return False
    
    def import_changes(self, file_path: str) -> bool:
        """Import change history from file"""
        try:
            import json
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Import tracked files
            if 'tracked_files' in data:
                self.tracked_files = set(data['tracked_files'])
            
            # Import changes
            if 'changes' in data:
                self.change_history = []
                for change_data in data['changes']:
                    change = FileChangeEvent.from_dict(change_data)
                    self.change_history.append(change)
            
            logger.info(f"Imported {len(self.change_history)} changes from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing changes: {e}")
            return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate hash for file"""
        try:
            import hashlib
            
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def _update_file_hash(self, file_path: str) -> None:
        """Update hash for file"""
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                self.file_hashes[file_path] = self._calculate_file_hash(file_path_obj)
        except Exception as e:
            logger.error(f"Error updating hash for {file_path}: {e}")
    
    def get_tracking_stats(self) -> Dict[str, Any]:
        """Get change tracking statistics"""
        return {
            'tracking_stats': self.stats.copy(),
            'files_tracked': len(self.tracked_files),
            'total_changes': len(self.change_history),
            'tracked_files_list': list(self.tracked_files),
            'recent_changes_count': len(self.get_recent_changes(10))
        }
    
    def is_healthy(self) -> bool:
        """Check if change tracker is healthy"""
        try:
            # Check if git operations are healthy
            if not self.git_operations.is_healthy():
                return False
            
            # Check if we can access tracked files
            for file_path in list(self.tracked_files)[:5]:  # Check first 5 files
                if not Path(file_path).exists() and file_path in self.file_hashes:
                    # File was deleted, this is normal
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators"""
        try:
            return {
                'tracker_healthy': self.is_healthy(),
                'git_operations_healthy': self.git_operations.is_healthy(),
                'tracking_stats': self.stats,
                'files_tracked': len(self.tracked_files),
                'total_changes': len(self.change_history),
                'last_scan_time': self.stats['last_scan_time']
            }
        except Exception as e:
            return {
                'tracker_healthy': False,
                'error': str(e)
            }
