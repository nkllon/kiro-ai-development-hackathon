#!/usr/bin/env python3
"""
File Watcher - High-level file monitoring interface

Composed from FileWatcherCore for RM-DDD compliance.
Single responsibility: High-level file monitoring interface and coordination.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any

from .models import FileChangeEvent, ChangeType, ContentType, DevpostConfig
from .file_watcher_core import FileWatcherCore

logger = logging.getLogger(__name__)


class ProjectFileMonitor:
    """
    High-level project file monitor for Devpost integration.
    
    Provides a clean interface for file monitoring while delegating
    core functionality to specialized components.
    """
    
    def __init__(
        self,
        project_path: Path,
        sync_manager: Optional[Any] = None,
        config: Optional[DevpostConfig] = None
    ):
        """
        Initialize project file monitor.
        
        Args:
            project_path: Path to the project directory to monitor
            sync_manager: Optional sync manager for handling changes
            config: Optional configuration object
        """
        self.project_path = Path(project_path).resolve()
        self.sync_manager = sync_manager
        self.config = config or DevpostConfig()
        
        # Initialize core watcher
        self.core_watcher = FileWatcherCore(project_path, config)
        
        # High-level statistics
        self.stats = {
            'total_changes': 0,
            'significant_changes': 0,
            'last_activity': None
        }
    
    def add_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Add callback for file change events."""
        self.core_watcher.add_change_callback(callback)
    
    def remove_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Remove callback for file change events."""
        self.core_watcher.remove_change_callback(callback)
    
    def start_monitoring(self) -> bool:
        """Start file system monitoring."""
        logger.info(f"Starting file monitoring for {self.project_path}")
        
        # Add internal change handler
        self.core_watcher.add_change_callback(self._handle_file_change)
        
        # Start core monitoring
        success = self.core_watcher.start_monitoring()
        
        if success:
            logger.info("File monitoring started successfully")
        else:
            logger.error("Failed to start file monitoring")
        
        return success
    
    def stop_monitoring(self) -> bool:
        """Stop file system monitoring."""
        logger.info("Stopping file monitoring...")
        
        # Remove internal change handler
        self.core_watcher.remove_change_callback(self._handle_file_change)
        
        # Stop core monitoring
        success = self.core_watcher.stop_monitoring()
        
        if success:
            logger.info("File monitoring stopped successfully")
        else:
            logger.error("Failed to stop file monitoring")
        
        return success
    
    def _handle_file_change(self, event: FileChangeEvent) -> None:
        """Handle file change event with high-level processing."""
        try:
            self.stats['total_changes'] += 1
            self.stats['last_activity'] = event.timestamp
            
            # Determine if change is significant
            if self._is_significant_change(event):
                self.stats['significant_changes'] += 1
                self._handle_significant_change(event)
            else:
                self._handle_standard_change(event)
            
            # Notify sync manager if available
            if self.sync_manager:
                self._notify_sync_manager(event)
            
            logger.debug(f"Processed change: {event.file_path.name} ({event.change_type.value})")
            
        except Exception as e:
            logger.error(f"Error handling file change: {e}")
    
    def _is_significant_change(self, event: FileChangeEvent) -> bool:
        """Determine if file change is significant."""
        # Code files are always significant
        if event.content_type == ContentType.CODE:
            return True
        
        # Media files are significant
        if event.content_type in [ContentType.IMAGE, ContentType.VIDEO, ContentType.AUDIO]:
            return True
        
        # Documentation changes are significant
        if event.content_type == ContentType.DOCUMENTATION:
            return True
        
        # New files are significant
        if event.change_type == ChangeType.CREATED:
            return True
        
        # Deleted files are significant
        if event.change_type == ChangeType.DELETED:
            return True
        
        return False
    
    def _handle_significant_change(self, event: FileChangeEvent) -> None:
        """Handle significant file changes."""
        logger.info(f"Significant change detected: {event.file_path.name}")
        
        # Log change details
        logger.debug(f"Change type: {event.change_type.value}")
        logger.debug(f"Content type: {event.content_type.value}")
        logger.debug(f"Timestamp: {event.timestamp}")
    
    def _handle_standard_change(self, event: FileChangeEvent) -> None:
        """Handle standard file changes."""
        logger.debug(f"Standard change: {event.file_path.name}")
    
    def _notify_sync_manager(self, event: FileChangeEvent) -> None:
        """Notify sync manager of file change."""
        try:
            if hasattr(self.sync_manager, 'handle_file_change'):
                self.sync_manager.handle_file_change(event)
            elif hasattr(self.sync_manager, 'sync_file'):
                self.sync_manager.sync_file(event.file_path)
        except Exception as e:
            logger.error(f"Error notifying sync manager: {e}")
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get comprehensive monitoring statistics."""
        core_stats = self.core_watcher.get_monitoring_stats()
        
        return {
            **self.stats,
            **core_stats,
            'monitoring_active': self.core_watcher.is_monitoring,
            'project_path': str(self.project_path)
        }
    
    def get_file_status(self, file_path: Path) -> Dict[str, Any]:
        """Get status information for specific file."""
        file_str = str(file_path)
        
        return {
            'is_tracked': file_str in self.core_watcher.file_hashes,
            'last_modified': self.core_watcher.file_timestamps.get(file_str),
            'file_hash': self.core_watcher.file_hashes.get(file_str),
            'is_ignored': self.core_watcher._should_ignore_file(file_path)
        }
    
    def force_scan(self) -> bool:
        """Force a complete rescan of all files."""
        logger.info("Forcing complete file rescan...")
        
        try:
            # Clear existing tracking
            self.core_watcher.file_hashes.clear()
            self.core_watcher.file_timestamps.clear()
            
            # Perform new scan
            self.core_watcher._perform_initial_scan()
            
            logger.info("File rescan completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during file rescan: {e}")
            return False
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is currently active."""
        return self.core_watcher.is_monitoring
    
    def get_pending_changes(self) -> List[FileChangeEvent]:
        """Get list of pending file changes."""
        return list(self.core_watcher.pending_changes.values())
    
    def clear_pending_changes(self) -> None:
        """Clear all pending file changes."""
        self.core_watcher.pending_changes.clear()
        logger.info("Cleared all pending changes")