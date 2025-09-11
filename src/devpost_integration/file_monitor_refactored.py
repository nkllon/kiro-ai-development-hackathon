#!/usr/bin/env python3
"""
Project File Monitor - Refactored for RM-DDD Compliance

Composed from decomposed modules for single responsibility compliance.
Maintains all original functionality while meeting 200-line limit.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any

from .models import FileChangeEvent, ChangeType, ContentType, DevpostConfig
from .file_watcher import ProjectFileMonitor, ProjectFileEventHandler
from .change_detector import ContentBasedChangeDetector
from .media_detector import MediaFileDetector
from .git_integration import GitIntegration

logger = logging.getLogger(__name__)


class ProjectFileMonitorRefactored:
    """
    Refactored project file monitor for Devpost integration.
    
    Composed from specialized modules to maintain single responsibility
    while providing comprehensive file monitoring capabilities.
    """
    
    def __init__(
        self,
        project_path: Path,
        sync_manager: Optional[Any] = None,
        config: Optional[DevpostConfig] = None
    ):
        """
        Initialize refactored project file monitor.
        
        Args:
            project_path: Path to the project directory to monitor
            sync_manager: Optional sync manager for handling changes
            config: Optional configuration object
        """
        self.project_path = Path(project_path).resolve()
        self.sync_manager = sync_manager
        self.config = config or DevpostConfig()
        
        # Initialize specialized components
        self.file_watcher = ProjectFileMonitor(project_path, sync_manager, config)
        self.change_detector = ContentBasedChangeDetector()
        self.media_detector = MediaFileDetector()
        self.git_integration = GitIntegration(project_path, config)
        
        # Statistics
        self.stats = {
            'total_changes': 0,
            'significant_changes': 0,
            'media_changes': 0,
            'git_commits': 0,
            'last_analysis': None
        }
    
    def start_monitoring(self) -> bool:
        """Start comprehensive file monitoring."""
        logger.info("Starting refactored file monitoring...")
        
        # Start file watching
        if not self.file_watcher.start_monitoring():
            return False
        
        # Initialize git repository if needed
        if not self.git_integration.is_git_repo:
            logger.info("Initializing git repository...")
            self.git_integration.initialize_git_repository()
        
        # Add change processing callback
        self.file_watcher.add_change_callback(self._process_file_change)
        
        logger.info("Refactored file monitoring started successfully")
        return True
    
    def stop_monitoring(self) -> bool:
        """Stop file monitoring."""
        logger.info("Stopping refactored file monitoring...")
        
        # Stop file watching
        success = self.file_watcher.stop_monitoring()
        
        # Remove change callback
        self.file_watcher.remove_change_callback(self._process_file_change)
        
        logger.info("Refactored file monitoring stopped")
        return success
    
    def _process_file_change(self, event: FileChangeEvent) -> None:
        """Process file change event with specialized analyzers."""
        try:
            self.stats['total_changes'] += 1
            
            # Analyze change significance
            is_significant, significance_score = self.change_detector.analyze_change_significance(event)
            if is_significant:
                self.stats['significant_changes'] += 1
            
            # Check if it's a media file
            if self.media_detector.is_media_file(event.file_path):
                self.stats['media_changes'] += 1
                self._handle_media_change(event)
            
            # Categorize change
            categorization = self.change_detector.categorize_change(event)
            
            # Handle based on categorization
            if categorization['recommended_action'] == 'sync_immediately':
                self._handle_immediate_sync(event, categorization)
            elif categorization['recommended_action'] == 'sync_and_validate':
                self._handle_sync_with_validation(event, categorization)
            elif categorization['recommended_action'] == 'sync':
                self._handle_standard_sync(event, categorization)
            
            # Git integration if enabled
            if self.git_integration.auto_commit:
                self._handle_git_operations([event])
            
            logger.debug(f"Processed change: {event.file_path.name} ({event.change_type.value})")
            
        except Exception as e:
            logger.error(f"Error processing file change: {e}")
    
    def _handle_media_change(self, event: FileChangeEvent) -> None:
        """Handle media file changes."""
        try:
            if event.change_type == ChangeType.CREATED:
                # Validate new media file
                is_valid, error_msg = self.media_detector.validate_media_file(event.file_path)
                if not is_valid:
                    logger.warning(f"Invalid media file {event.file_path}: {error_msg}")
                    return
                
                # Extract metadata
                media_file = self.media_detector.create_media_file(event.file_path)
                if media_file:
                    logger.info(f"New media file detected: {media_file.media_type.value} - {event.file_path.name}")
            
            elif event.change_type == ChangeType.MODIFIED:
                # Re-validate modified media file
                is_valid, error_msg = self.media_detector.validate_media_file(event.file_path)
                if not is_valid:
                    logger.warning(f"Media file became invalid: {event.file_path}: {error_msg}")
                    return
                
                logger.info(f"Media file modified: {event.file_path.name}")
            
            elif event.change_type == ChangeType.DELETED:
                logger.info(f"Media file deleted: {event.file_path.name}")
                
        except Exception as e:
            logger.error(f"Error handling media change: {e}")
    
    def _handle_immediate_sync(self, event: FileChangeEvent, categorization: Dict[str, Any]) -> None:
        """Handle immediate synchronization."""
        logger.info(f"Immediate sync required for {event.file_path.name}")
        
        if self.sync_manager:
            try:
                self.sync_manager.sync_file_immediately(event.file_path)
            except Exception as e:
                logger.error(f"Immediate sync failed: {e}")
    
    def _handle_sync_with_validation(self, event: FileChangeEvent, categorization: Dict[str, Any]) -> None:
        """Handle sync with validation."""
        logger.info(f"Sync with validation for {event.file_path.name}")
        
        if self.sync_manager:
            try:
                # Validate before sync
                if categorization['is_code']:
                    self._validate_code_file(event.file_path)
                elif categorization['is_config']:
                    self._validate_config_file(event.file_path)
                
                self.sync_manager.sync_file_with_validation(event.file_path)
            except Exception as e:
                logger.error(f"Sync with validation failed: {e}")
    
    def _handle_standard_sync(self, event: FileChangeEvent, categorization: Dict[str, Any]) -> None:
        """Handle standard synchronization."""
        logger.debug(f"Standard sync for {event.file_path.name}")
        
        if self.sync_manager:
            try:
                self.sync_manager.sync_file(event.file_path)
            except Exception as e:
                logger.error(f"Standard sync failed: {e}")
    
    def _handle_git_operations(self, events: List[FileChangeEvent]) -> None:
        """Handle git operations for file changes."""
        try:
            if self.git_integration.handle_file_changes(events):
                self.stats['git_commits'] += 1
        except Exception as e:
            logger.error(f"Git operations failed: {e}")
    
    def _validate_code_file(self, file_path: Path) -> bool:
        """Validate code file before sync."""
        try:
            # Basic syntax validation for Python files
            if file_path.suffix == '.py':
                with open(file_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(file_path), 'exec')
            return True
        except Exception as e:
            logger.error(f"Code validation failed for {file_path}: {e}")
            return False
    
    def _validate_config_file(self, file_path: Path) -> bool:
        """Validate configuration file before sync."""
        try:
            # Basic JSON validation
            if file_path.suffix == '.json':
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            return True
        except Exception as e:
            logger.error(f"Config validation failed for {file_path}: {e}")
            return False
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive monitoring statistics."""
        return {
            **self.stats,
            'file_watcher_stats': self.file_watcher.get_monitoring_stats(),
            'git_stats': self.git_integration.get_git_statistics(),
            'supported_media_formats': self.media_detector.get_supported_formats()
        }
    
    def analyze_recent_changes(self, limit: int = 100) -> Dict[str, Any]:
        """Analyze recent file changes."""
        # This would integrate with the change detector's analysis capabilities
        # For now, return basic stats
        return {
            'total_changes': self.stats['total_changes'],
            'significant_changes': self.stats['significant_changes'],
            'media_changes': self.stats['media_changes'],
            'git_commits': self.stats['git_commits']
        }
    
    def add_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Add callback for file change events."""
        self.file_watcher.add_change_callback(callback)
    
    def remove_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Remove callback for file change events."""
        self.file_watcher.remove_change_callback(callback)
