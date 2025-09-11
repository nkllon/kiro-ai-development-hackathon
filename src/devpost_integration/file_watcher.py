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
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime


logger = logging.getLogger(__name__)

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'File Watcher',
            'description': 'file_watcher module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return []
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
            # Add module-specific health checks here
            
            
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
            logger.error(f"Health check failed: {e}")
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
            parameters={},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {self.module_id} module")


class ProjectFileMonitor(ReflectiveModule):
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