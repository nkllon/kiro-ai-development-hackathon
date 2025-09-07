#!/usr/bin/env python3
"""
Project File Monitor for Devpost Integration

The Requirements ARE the Solution - Intelligent File Change Detection
"""

import asyncio
import hashlib
import logging
import mimetypes
import os
import re
import subprocess
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Callable, Any, Tuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .models import (
    FileChangeEvent, ChangeType, ContentType, SyncOperation, 
    SyncOperationType, DevpostConfig, MediaType, MediaFile
)


logger = logging.getLogger(__name__)


class ProjectFileMonitor:
    """
    Intelligent file system monitor for Devpost project synchronization.
    
    Monitors project files for changes, filters relevant modifications,
    implements debouncing to prevent excessive sync operations, and
    categorizes changes by content type for targeted synchronization.
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
            project_path: Root path of the project to monitor
            sync_manager: Optional sync manager for triggering sync operations
            config: Optional project configuration for watch patterns
        """
        self.project_path = project_path.resolve()
        self.sync_manager = sync_manager
        self.config = config or DevpostConfig("", "")
        
        # Monitoring state
        self._observer: Optional[Observer] = None
        self._event_handler: Optional['ProjectFileEventHandler'] = None
        self._is_monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Change tracking
        self._change_queue: deque = deque(maxlen=1000)  # Limit queue size
        self._recent_changes: Dict[str, FileChangeEvent] = {}
        self._debounce_timers: Dict[str, threading.Timer] = {}
        
        # Configuration
        self.debounce_delay = 2.0  # seconds
        self.batch_size = 10
        self.max_queue_age = timedelta(hours=1)
        
        # Watch patterns
        self.watch_patterns = self._get_watch_patterns()
        self.ignore_patterns = self._get_ignore_patterns()
        
        # Content type detection
        self.content_type_mappings = self._build_content_type_mappings()
        
        # Intelligent change detection components (Task 6.2)
        self.content_detector = ContentBasedChangeDetector()
        self.media_detector = MediaFileDetector()
        self.git_integration = GitIntegration(self.project_path)
        
        # Statistics
        self._stats = {
            "total_events": 0,
            "filtered_events": 0,
            "debounced_events": 0,
            "sync_triggered": 0,
            "errors": 0,
            "content_analyzed": 0,
            "media_detected": 0,
            "releases_detected": 0
        }
        
        logger.info(f"ProjectFileMonitor initialized for {self.project_path}")
    
    def _get_watch_patterns(self) -> List[str]:
        """Get file patterns to watch for changes."""
        if self.config and self.config.watch_patterns and len(self.config.watch_patterns) > 0:
            return self.config.watch_patterns
        
        # Default patterns for common project files
        return [
            "*.md", "*.txt", "*.rst",  # Documentation
            "*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c", "*.go", "*.rs",  # Source code
            "*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg",  # Configuration
            "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg",  # Images
            "*.mp4", "*.mov", "*.avi", "*.webm",  # Videos
            "*.pdf", "*.doc", "*.docx",  # Documents
            "package.json", "requirements.txt", "Cargo.toml", "pom.xml",  # Dependencies
            "README*", "LICENSE*", "CHANGELOG*", "CONTRIBUTING*"  # Project files
        ]
    
    def _get_ignore_patterns(self) -> List[str]:
        """Get file patterns to ignore."""
        return [
            "*.pyc", "*.pyo", "*.pyd", "__pycache__/*",  # Python bytecode
            "*.class", "*.jar",  # Java bytecode
            "*.o", "*.so", "*.dll", "*.dylib",  # Compiled binaries
            ".git/*", ".svn/*", ".hg/*",  # Version control
            "node_modules/*", "venv/*", "env/*", ".env/*",  # Dependencies/environments
            ".DS_Store", "Thumbs.db", "*.tmp", "*.temp",  # System files
            "*.log", "*.cache",  # Log and cache files
            ".pytest_cache/*", ".coverage", "htmlcov/*",  # Test artifacts
            "dist/*", "build/*", "target/*", "out/*",  # Build outputs
            ".idea/*", ".vscode/*", "*.swp", "*.swo",  # Editor files
            ".devpost/*"  # Our own config directory
        ]
    
    def _build_content_type_mappings(self) -> Dict[str, ContentType]:
        """Build mapping from file extensions to content types."""
        return {
            # Documentation
            ".md": ContentType.DOCUMENTATION,
            ".txt": ContentType.DOCUMENTATION,
            ".rst": ContentType.DOCUMENTATION,
            ".adoc": ContentType.DOCUMENTATION,
            
            # Media files
            ".png": ContentType.MEDIA,
            ".jpg": ContentType.MEDIA,
            ".jpeg": ContentType.MEDIA,
            ".gif": ContentType.MEDIA,
            ".svg": ContentType.MEDIA,
            ".mp4": ContentType.MEDIA,
            ".mov": ContentType.MEDIA,
            ".avi": ContentType.MEDIA,
            ".webm": ContentType.MEDIA,
            ".pdf": ContentType.MEDIA,
            
            # Source code
            ".py": ContentType.SOURCE_CODE,
            ".js": ContentType.SOURCE_CODE,
            ".ts": ContentType.SOURCE_CODE,
            ".java": ContentType.SOURCE_CODE,
            ".cpp": ContentType.SOURCE_CODE,
            ".c": ContentType.SOURCE_CODE,
            ".go": ContentType.SOURCE_CODE,
            ".rs": ContentType.SOURCE_CODE,
            ".php": ContentType.SOURCE_CODE,
            ".rb": ContentType.SOURCE_CODE,
            ".swift": ContentType.SOURCE_CODE,
            ".kt": ContentType.SOURCE_CODE,
            
            # Configuration
            ".json": ContentType.CONFIGURATION,
            ".yaml": ContentType.CONFIGURATION,
            ".yml": ContentType.CONFIGURATION,
            ".toml": ContentType.CONFIGURATION,
            ".ini": ContentType.CONFIGURATION,
            ".cfg": ContentType.CONFIGURATION,
            ".conf": ContentType.CONFIGURATION,
            ".env": ContentType.CONFIGURATION,
        }
    
    def start_monitoring(self) -> None:
        """Start monitoring project files for changes."""
        if self._is_monitoring:
            logger.warning("File monitoring is already active")
            return
        
        try:
            # Validate project path
            if not self.project_path.exists():
                raise ValueError(f"Project path does not exist: {self.project_path}")
            
            if not self.project_path.is_dir():
                raise ValueError(f"Project path is not a directory: {self.project_path}")
            
            # Create event handler
            self._event_handler = ProjectFileEventHandler(self)
            
            # Create and configure observer
            self._observer = Observer()
            self._observer.schedule(
                self._event_handler,
                str(self.project_path),
                recursive=True
            )
            
            # Start observer
            self._observer.start()
            self._is_monitoring = True
            
            logger.info(f"Started file monitoring for {self.project_path}")
            
        except Exception as e:
            logger.error(f"Failed to start file monitoring: {e}")
            self._cleanup_monitoring()
            raise
    
    def stop_monitoring(self) -> None:
        """Stop monitoring project files."""
        if not self._is_monitoring:
            logger.debug("File monitoring is not active")
            return
        
        try:
            self._is_monitoring = False
            
            # Stop observer
            if self._observer:
                self._observer.stop()
                self._observer.join(timeout=5.0)
                if self._observer.is_alive():
                    logger.warning("Observer thread did not stop gracefully")
            
            # Cancel pending debounce timers
            for timer in self._debounce_timers.values():
                timer.cancel()
            self._debounce_timers.clear()
            
            # Clear state
            self._cleanup_monitoring()
            
            logger.info("Stopped file monitoring")
            
        except Exception as e:
            logger.error(f"Error stopping file monitoring: {e}")
            self._cleanup_monitoring()
    
    def _cleanup_monitoring(self) -> None:
        """Clean up monitoring resources."""
        self._observer = None
        self._event_handler = None
        self._is_monitoring = False
        self._recent_changes.clear()
        self._debounce_timers.clear()
    
    def add_watch_path(self, path: Path) -> None:
        """
        Add additional path to monitoring.
        
        Args:
            path: Path to add to monitoring
        """
        if not self._observer or not self._is_monitoring:
            logger.warning("Cannot add watch path: monitoring not active")
            return
        
        try:
            resolved_path = path.resolve()
            
            # Ensure path is within project directory
            if not self._is_path_within_project(resolved_path):
                logger.warning(f"Path {resolved_path} is outside project directory")
                return
            
            # Add to observer
            self._observer.schedule(
                self._event_handler,
                str(resolved_path),
                recursive=True
            )
            
            logger.info(f"Added watch path: {resolved_path}")
            
        except Exception as e:
            logger.error(f"Failed to add watch path {path}: {e}")
    
    def remove_watch_path(self, path: Path) -> None:
        """
        Remove path from monitoring.
        
        Args:
            path: Path to remove from monitoring
        """
        if not self._observer or not self._is_monitoring:
            logger.warning("Cannot remove watch path: monitoring not active")
            return
        
        try:
            resolved_path = path.resolve()
            
            # Find and remove watch
            for watch in self._observer.emitters:
                if Path(watch.watch.path) == resolved_path:
                    self._observer.unschedule(watch.watch)
                    logger.info(f"Removed watch path: {resolved_path}")
                    return
            
            logger.warning(f"Watch path not found: {resolved_path}")
            
        except Exception as e:
            logger.error(f"Failed to remove watch path {path}: {e}")
    
    def get_recent_changes(self, limit: Optional[int] = None) -> List[FileChangeEvent]:
        """
        Get recent file changes.
        
        Args:
            limit: Maximum number of changes to return
            
        Returns:
            List of recent FileChangeEvent objects
        """
        # Clean up old changes
        self._cleanup_old_changes()
        
        # Get changes from queue
        changes = list(self._change_queue)
        
        # Sort by timestamp (most recent first)
        changes.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit if specified
        if limit:
            changes = changes[:limit]
        
        return changes
    
    def get_change_events(self) -> List[FileChangeEvent]:
        """Get all pending change events and clear the queue."""
        changes = list(self._change_queue)
        self._change_queue.clear()
        return changes
    
    def handle_file_change(self, event: FileSystemEvent) -> None:
        """
        Handle file system change event.
        
        Args:
            event: File system event from watchdog
        """
        try:
            self._stats["total_events"] += 1
            
            # Convert watchdog event to our event format
            file_path = Path(event.src_path)
            
            # Filter out irrelevant changes
            if not self._should_process_change(file_path, event):
                self._stats["filtered_events"] += 1
                return
            
            # Determine change type
            change_type = self._get_change_type(event)
            
            # Determine content type
            content_type = self._get_content_type(file_path)
            
            # Check if change affects sync
            affects_sync = self._affects_sync(file_path, content_type)
            
            # Create change event
            change_event = FileChangeEvent(
                file_path=file_path,
                change_type=change_type,
                timestamp=datetime.now(),
                affects_sync=affects_sync,
                content_type=content_type
            )
            
            # Apply debouncing
            self._debounce_change(change_event)
            
        except Exception as e:
            logger.error(f"Error handling file change: {e}")
            self._stats["errors"] += 1
    
    def _should_process_change(self, file_path: Path, event: FileSystemEvent) -> bool:
        """
        Determine if a file change should be processed.
        
        Args:
            file_path: Path of changed file
            event: File system event
            
        Returns:
            True if change should be processed
        """
        # Check if path is within project
        if not self._is_path_within_project(file_path):
            return False
        
        # Check ignore patterns
        try:
            relative_path = file_path.resolve().relative_to(self.project_path.resolve())
            relative_path_str = str(relative_path)
        except ValueError:
            # Path is not within project
            return False
        
        for pattern in self.ignore_patterns:
            if self._matches_pattern(relative_path_str, pattern):
                return False
        
        # Check watch patterns (if file, not directory)
        if file_path.is_file():
            for pattern in self.watch_patterns:
                if self._matches_pattern(file_path.name, pattern):
                    return True
            
            # Special handling for important project files
            if file_path.name.upper().startswith(('README', 'LICENSE', 'CHANGELOG', 'CONTRIBUTING')):
                return True
        
        # For directories, only process if they contain relevant files
        elif file_path.is_dir():
            return True  # Let directory events through for now
        
        return False
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """
        Check if filename matches a glob pattern.
        
        Args:
            filename: Filename to check
            pattern: Glob pattern
            
        Returns:
            True if filename matches pattern
        """
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def _is_path_within_project(self, path: Path) -> bool:
        """
        Check if path is within the project directory.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is within project
        """
        try:
            path.resolve().relative_to(self.project_path)
            return True
        except ValueError:
            return False
    
    def _get_change_type(self, event: FileSystemEvent) -> ChangeType:
        """
        Convert watchdog event type to our ChangeType enum.
        
        Args:
            event: Watchdog file system event
            
        Returns:
            ChangeType enum value
        """
        if event.event_type == 'created':
            return ChangeType.CREATED
        elif event.event_type == 'modified':
            return ChangeType.MODIFIED
        elif event.event_type == 'deleted':
            return ChangeType.DELETED
        elif event.event_type == 'moved':
            return ChangeType.RENAMED
        else:
            return ChangeType.MODIFIED  # Default fallback
    
    def _get_content_type(self, file_path: Path) -> ContentType:
        """
        Determine content type based on file extension and name.
        
        Args:
            file_path: Path of the file
            
        Returns:
            ContentType enum value
        """
        # Check file extension
        extension = file_path.suffix.lower()
        if extension in self.content_type_mappings:
            return self.content_type_mappings[extension]
        
        # Check special file names
        filename = file_path.name.upper()
        if filename.startswith(('README', 'CHANGELOG', 'CONTRIBUTING', 'LICENSE')):
            return ContentType.DOCUMENTATION
        
        # Check for release/version files
        if filename in ('VERSION', 'RELEASE', 'RELEASES'):
            return ContentType.RELEASE
        
        # Default to source code
        return ContentType.SOURCE_CODE
    
    def _affects_sync(self, file_path: Path, content_type: ContentType) -> bool:
        """
        Determine if a file change should trigger synchronization using intelligent detection.
        
        Args:
            file_path: Path of changed file
            content_type: Content type of the file
            
        Returns:
            True if change should trigger sync
        """
        # Use content-based change detection for documentation
        if content_type == ContentType.DOCUMENTATION:
            is_significant = self.content_detector.is_significant_change(file_path, content_type)
            if is_significant:
                self._stats["content_analyzed"] += 1
            return is_significant
        
        # Media files always trigger sync (but check if it's actually media)
        if content_type == ContentType.MEDIA:
            media_file = self.media_detector.detect_media_files(file_path)
            if media_file:
                self._stats["media_detected"] += 1
                return True
            return False
        
        # Release/version changes trigger sync
        if content_type == ContentType.RELEASE:
            return True
        
        # Important project files - use content detection
        filename = file_path.name.upper()
        if filename.startswith(('README', 'LICENSE', 'CHANGELOG')):
            is_significant = self.content_detector.is_significant_change(file_path, ContentType.DOCUMENTATION)
            if is_significant:
                self._stats["content_analyzed"] += 1
            return is_significant
        
        # Configuration files that might affect project metadata
        if filename in ('PACKAGE.JSON', 'PYPROJECT.TOML', 'CARGO.TOML', 'POM.XML'):
            # Check if version or important metadata changed
            return self._check_metadata_file_changes(file_path)
        
        # Source code changes might trigger sync depending on configuration
        if content_type == ContentType.SOURCE_CODE:
            return self.config.sync_enabled if self.config else False
        
        return False
    
    def _debounce_change(self, change_event: FileChangeEvent) -> None:
        """
        Apply debouncing to file change events.
        
        Args:
            change_event: File change event to debounce
        """
        file_key = str(change_event.file_path)
        
        # Cancel existing timer for this file
        if file_key in self._debounce_timers:
            self._debounce_timers[file_key].cancel()
        
        # Store the most recent change
        self._recent_changes[file_key] = change_event
        
        # Create new debounce timer
        timer = threading.Timer(
            self.debounce_delay,
            self._process_debounced_change,
            args=[file_key]
        )
        
        self._debounce_timers[file_key] = timer
        timer.start()
        
        self._stats["debounced_events"] += 1
    
    def _process_debounced_change(self, file_key: str) -> None:
        """
        Process a debounced file change.
        
        Args:
            file_key: File path key for the change
        """
        try:
            # Get the change event
            if file_key not in self._recent_changes:
                return
            
            change_event = self._recent_changes.pop(file_key)
            
            # Remove timer
            if file_key in self._debounce_timers:
                del self._debounce_timers[file_key]
            
            # Add to change queue
            self._change_queue.append(change_event)
            
            # Trigger sync if needed
            if change_event.affects_sync and self.sync_manager:
                try:
                    self.sync_manager.queue_sync_operation(
                        SyncOperation(
                            operation_type=self._get_sync_operation_type(change_event),
                            target_field=self._get_target_field(change_event),
                            local_value=str(change_event.file_path),
                            remote_value=None,
                            timestamp=change_event.timestamp
                        )
                    )
                    self._stats["sync_triggered"] += 1
                except Exception as e:
                    logger.error(f"Failed to queue sync operation: {e}")
            
            logger.debug(f"Processed change: {change_event.file_path} ({change_event.change_type})")
            
        except Exception as e:
            logger.error(f"Error processing debounced change: {e}")
            self._stats["errors"] += 1
    
    def _get_sync_operation_type(self, change_event: FileChangeEvent) -> SyncOperationType:
        """
        Determine sync operation type based on change event.
        
        Args:
            change_event: File change event
            
        Returns:
            SyncOperationType enum value
        """
        if change_event.content_type == ContentType.MEDIA:
            return SyncOperationType.UPLOAD_MEDIA
        elif change_event.content_type == ContentType.DOCUMENTATION:
            return SyncOperationType.UPDATE_DESCRIPTION
        else:
            return SyncOperationType.UPDATE_METADATA
    
    def _get_target_field(self, change_event: FileChangeEvent) -> str:
        """
        Determine target field for sync operation.
        
        Args:
            change_event: File change event
            
        Returns:
            Target field name
        """
        filename = change_event.file_path.name.upper()
        
        if filename.startswith('README'):
            return 'description'
        elif change_event.content_type == ContentType.MEDIA:
            return 'media'
        elif filename.startswith('CHANGELOG'):
            return 'changelog'
        else:
            return 'metadata'
    
    def _cleanup_old_changes(self) -> None:
        """Remove old changes from tracking."""
        cutoff_time = datetime.now() - self.max_queue_age
        
        # Clean up change queue
        while self._change_queue and self._change_queue[0].timestamp < cutoff_time:
            self._change_queue.popleft()
        
        # Clean up recent changes
        expired_keys = [
            key for key, change in self._recent_changes.items()
            if change.timestamp < cutoff_time
        ]
        
        for key in expired_keys:
            del self._recent_changes[key]
    
    def _check_metadata_file_changes(self, file_path: Path) -> bool:
        """
        Check if changes in metadata files are significant.
        
        Args:
            file_path: Path to metadata file
            
        Returns:
            True if changes affect project metadata
        """
        try:
            filename = file_path.name.lower()
            
            if filename == 'package.json':
                return self._check_package_json_changes(file_path)
            elif filename in ['pyproject.toml', 'setup.py']:
                return self._check_python_metadata_changes(file_path)
            elif filename == 'cargo.toml':
                return self._check_cargo_metadata_changes(file_path)
            elif filename == 'pom.xml':
                return self._check_maven_metadata_changes(file_path)
                
        except Exception as e:
            logger.warning(f"Error checking metadata file changes for {file_path}: {e}")
            # Default to significant change on error
            return True
        
        return False
    
    def _check_package_json_changes(self, file_path: Path) -> bool:
        """Check for significant changes in package.json."""
        try:
            import json
            content = file_path.read_text(encoding='utf-8')
            data = json.loads(content)
            
            # Check for changes in important fields
            important_fields = ['name', 'version', 'description', 'keywords', 'author', 'license']
            
            file_key = f"{file_path}_metadata"
            previous_data = getattr(self, '_previous_metadata', {}).get(file_key, {})
            
            # Store current data
            if not hasattr(self, '_previous_metadata'):
                self._previous_metadata = {}
            self._previous_metadata[file_key] = {field: data.get(field) for field in important_fields}
            
            # Check for changes
            for field in important_fields:
                if data.get(field) != previous_data.get(field):
                    return True
                    
        except Exception as e:
            logger.debug(f"Error parsing package.json: {e}")
            return True
        
        return False
    
    def _check_python_metadata_changes(self, file_path: Path) -> bool:
        """Check for significant changes in Python metadata files."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Look for version, name, description changes
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            
            file_key = f"{file_path}_python_metadata"
            previous_data = getattr(self, '_previous_metadata', {}).get(file_key, {})
            
            current_data = {
                'version': version_match.group(1) if version_match else None,
                'name': name_match.group(1) if name_match else None
            }
            
            # Store current data
            if not hasattr(self, '_previous_metadata'):
                self._previous_metadata = {}
            self._previous_metadata[file_key] = current_data
            
            # Check for changes
            return current_data != previous_data
            
        except Exception as e:
            logger.debug(f"Error parsing Python metadata: {e}")
            return True
        
        return False
    
    def _check_cargo_metadata_changes(self, file_path: Path) -> bool:
        """Check for significant changes in Cargo.toml."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Simple TOML parsing for key fields
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            description_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
            
            file_key = f"{file_path}_cargo_metadata"
            previous_data = getattr(self, '_previous_metadata', {}).get(file_key, {})
            
            current_data = {
                'version': version_match.group(1) if version_match else None,
                'name': name_match.group(1) if name_match else None,
                'description': description_match.group(1) if description_match else None
            }
            
            # Store current data
            if not hasattr(self, '_previous_metadata'):
                self._previous_metadata = {}
            self._previous_metadata[file_key] = current_data
            
            # Check for changes
            return current_data != previous_data
            
        except Exception as e:
            logger.debug(f"Error parsing Cargo.toml: {e}")
            return True
        
        return False
    
    def _check_maven_metadata_changes(self, file_path: Path) -> bool:
        """Check for significant changes in pom.xml."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Simple XML parsing for key fields
            version_match = re.search(r'<version>([^<]+)</version>', content)
            name_match = re.search(r'<name>([^<]+)</name>', content)
            description_match = re.search(r'<description>([^<]+)</description>', content)
            
            file_key = f"{file_path}_maven_metadata"
            previous_data = getattr(self, '_previous_metadata', {}).get(file_key, {})
            
            current_data = {
                'version': version_match.group(1) if version_match else None,
                'name': name_match.group(1) if name_match else None,
                'description': description_match.group(1) if description_match else None
            }
            
            # Store current data
            if not hasattr(self, '_previous_metadata'):
                self._previous_metadata = {}
            self._previous_metadata[file_key] = current_data
            
            # Check for changes
            return current_data != previous_data
            
        except Exception as e:
            logger.debug(f"Error parsing pom.xml: {e}")
            return True
        
        return False
    
    def check_for_releases(self) -> List[Dict[str, Any]]:
        """
        Check for new Git releases and tags.
        
        Returns:
            List of new release information
        """
        releases = self.git_integration.check_for_releases()
        if releases:
            self._stats["releases_detected"] += len(releases)
            
            # Create release change events
            for release in releases:
                change_event = FileChangeEvent(
                    file_path=self.project_path / '.git',  # Represent as git directory
                    change_type=ChangeType.MODIFIED,
                    timestamp=datetime.now(),
                    affects_sync=True,
                    content_type=ContentType.RELEASE
                )
                
                # Add release metadata to the event
                change_event.release_info = release
                self._change_queue.append(change_event)
        
        return releases
    
    def get_media_files(self) -> List[MediaFile]:
        """
        Get all detected media files in the project.
        
        Returns:
            List of MediaFile objects
        """
        media_files = []
        
        try:
            # Scan project directory for media files
            for file_path in self.project_path.rglob('*'):
                if file_path.is_file():
                    # Skip ignored files
                    try:
                        relative_path = file_path.relative_to(self.project_path)
                        relative_path_str = str(relative_path)
                        
                        # Check if file should be ignored
                        should_ignore = False
                        for pattern in self.ignore_patterns:
                            if self._matches_pattern(relative_path_str, pattern):
                                should_ignore = True
                                break
                        
                        if should_ignore:
                            continue
                            
                        # Try to detect as media file
                        media_file = self.media_detector.detect_media_files(file_path)
                        if media_file:
                            media_files.append(media_file)
                            
                    except ValueError:
                        # File is not within project directory
                        continue
        
        except Exception as e:
            logger.error(f"Error scanning for media files: {e}")
        
        return media_files
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            **self._stats,
            "is_monitoring": self._is_monitoring,
            "project_path": str(self.project_path),
            "queue_size": len(self._change_queue),
            "pending_changes": len(self._recent_changes),
            "active_timers": len(self._debounce_timers),
            "watch_patterns": len(self.watch_patterns),
            "ignore_patterns": len(self.ignore_patterns),
            "git_repo": self.git_integration.is_git_repo,
            "known_tags": len(self.git_integration.known_tags)
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_monitoring()


class ContentBasedChangeDetector:
    """
    Intelligent content-based change detection for documentation files.
    
    Analyzes file content to determine if changes are significant enough
    to trigger synchronization operations.
    """
    
    def __init__(self):
        """Initialize content-based change detector."""
        self.content_hashes: Dict[str, str] = {}
        self.significant_change_threshold = 0.1  # 10% content change
        self.documentation_patterns = [
            r'#+\s+.*',  # Markdown headers
            r'\*\*.*\*\*',  # Bold text
            r'\[.*\]\(.*\)',  # Links
            r'```.*```',  # Code blocks
            r'!\[.*\]\(.*\)',  # Images
        ]
        
    def is_significant_change(self, file_path: Path, content_type: ContentType) -> bool:
        """
        Determine if a file change is significant enough to trigger sync.
        
        Args:
            file_path: Path to the changed file
            content_type: Type of content in the file
            
        Returns:
            True if change is significant
        """
        if not file_path.exists():
            # File was deleted - always significant
            return True
            
        if content_type != ContentType.DOCUMENTATION:
            # For non-documentation files, use simple existence check
            return True
            
        try:
            # Read current content
            current_content = file_path.read_text(encoding='utf-8', errors='ignore')
            current_hash = self._calculate_content_hash(current_content)
            
            file_key = str(file_path)
            previous_hash = self.content_hashes.get(file_key)
            
            # Store current hash for future comparisons
            self.content_hashes[file_key] = current_hash
            
            if previous_hash is None:
                # First time seeing this file - significant
                return True
                
            if current_hash == previous_hash:
                # No content change
                return False
                
            # For documentation files, analyze semantic changes
            return self._analyze_documentation_changes(file_path, current_content)
            
        except Exception as e:
            logger.warning(f"Error analyzing content changes for {file_path}: {e}")
            # Default to significant change on error
            return True
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate hash of normalized content."""
        # Normalize whitespace and line endings
        normalized = re.sub(r'\s+', ' ', content.strip())
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def _analyze_documentation_changes(self, file_path: Path, content: str) -> bool:
        """
        Analyze documentation content for significant changes.
        
        Args:
            file_path: Path to documentation file
            content: Current file content
            
        Returns:
            True if changes are significant
        """
        # Check for structural changes (headers, links, etc.)
        structural_elements = []
        for pattern in self.documentation_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            structural_elements.extend(matches)
        
        # Store structural signature
        structural_hash = hashlib.md5(
            ''.join(structural_elements).encode('utf-8')
        ).hexdigest()
        
        file_key = f"{file_path}_structure"
        previous_structural_hash = self.content_hashes.get(file_key)
        self.content_hashes[file_key] = structural_hash
        
        if previous_structural_hash is not None and structural_hash != previous_structural_hash:
            # Structural changes are always significant
            return True
        
        # Check content length changes
        word_count = len(content.split())
        word_key = f"{file_path}_words"
        previous_word_count = self.content_hashes.get(word_key, 0)
        self.content_hashes[word_key] = word_count
        
        if previous_word_count > 0:
            change_ratio = abs(word_count - previous_word_count) / previous_word_count
            if change_ratio > self.significant_change_threshold:
                return True
        
        # If no previous data, consider it significant (first time analysis)
        if previous_structural_hash is None:
            return True
        
        return False


class MediaFileDetector:
    """
    Media file detection and categorization system.
    
    Identifies media files, categorizes them by type, and extracts
    metadata for synchronization with Devpost.
    """
    
    def __init__(self):
        """Initialize media file detector."""
        self.media_extensions = {
            # Images
            '.png': MediaType.IMAGE,
            '.jpg': MediaType.IMAGE,
            '.jpeg': MediaType.IMAGE,
            '.gif': MediaType.IMAGE,
            '.svg': MediaType.IMAGE,
            '.bmp': MediaType.IMAGE,
            '.webp': MediaType.IMAGE,
            '.ico': MediaType.IMAGE,
            
            # Videos
            '.mp4': MediaType.VIDEO,
            '.mov': MediaType.VIDEO,
            '.avi': MediaType.VIDEO,
            '.webm': MediaType.VIDEO,
            '.mkv': MediaType.VIDEO,
            '.flv': MediaType.VIDEO,
            '.wmv': MediaType.VIDEO,
            '.m4v': MediaType.VIDEO,
            
            # Documents
            '.pdf': MediaType.DOCUMENT,
            '.doc': MediaType.DOCUMENT,
            '.docx': MediaType.DOCUMENT,
            '.ppt': MediaType.DOCUMENT,
            '.pptx': MediaType.DOCUMENT,
            '.xls': MediaType.DOCUMENT,
            '.xlsx': MediaType.DOCUMENT,
        }
        
        self.screenshot_patterns = [
            r'screenshot',
            r'screen_shot',
            r'capture',
            r'demo_image',
            r'app_preview',
        ]
        
        self.demo_patterns = [
            r'demo',
            r'preview',
            r'walkthrough',
            r'tutorial',
            r'showcase',
        ]
    
    def detect_media_files(self, file_path: Path) -> Optional[MediaFile]:
        """
        Detect and categorize media files.
        
        Args:
            file_path: Path to potential media file
            
        Returns:
            MediaFile object if file is media, None otherwise
        """
        if not file_path.exists() or not file_path.is_file():
            return None
            
        extension = file_path.suffix.lower()
        if extension not in self.media_extensions:
            return None
        
        try:
            # Get basic file info
            file_size = file_path.stat().st_size
            media_type = self.media_extensions[extension]
            
            # Refine media type based on filename patterns
            filename_lower = file_path.name.lower()
            
            if media_type == MediaType.IMAGE:
                if any(re.search(pattern, filename_lower) for pattern in self.screenshot_patterns):
                    media_type = MediaType.SCREENSHOT
            elif media_type == MediaType.VIDEO:
                if any(re.search(pattern, filename_lower) for pattern in self.demo_patterns):
                    media_type = MediaType.DEMO
            
            # Generate caption from filename
            caption = self._generate_caption(file_path)
            
            return MediaFile(
                filename=file_path.name,
                file_path=file_path,
                media_type=media_type,
                caption=caption,
                file_size=file_size
            )
            
        except Exception as e:
            logger.warning(f"Error detecting media file {file_path}: {e}")
            return None
    
    def _generate_caption(self, file_path: Path) -> str:
        """Generate a caption from filename."""
        # Remove extension and convert to readable format
        name = file_path.stem
        
        # Replace underscores and hyphens with spaces
        name = re.sub(r'[_-]', ' ', name)
        
        # Add spaces before capital letters
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in name.split())
    
    def get_media_metadata(self, media_file: MediaFile) -> Dict[str, Any]:
        """
        Extract additional metadata from media files.
        
        Args:
            media_file: MediaFile object
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            'filename': media_file.filename,
            'file_size': media_file.file_size,
            'media_type': media_file.media_type.value,
            'mime_type': mimetypes.guess_type(str(media_file.file_path))[0]
        }
        
        try:
            if media_file.media_type in [MediaType.IMAGE, MediaType.SCREENSHOT]:
                metadata.update(self._get_image_metadata(media_file.file_path))
            elif media_file.media_type in [MediaType.VIDEO, MediaType.DEMO]:
                metadata.update(self._get_video_metadata(media_file.file_path))
        except Exception as e:
            logger.warning(f"Error extracting metadata from {media_file.file_path}: {e}")
        
        return metadata
    
    def _get_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract image metadata."""
        metadata = {}
        
        try:
            # Try to get image dimensions using PIL if available
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    metadata['width'] = img.width
                    metadata['height'] = img.height
                    metadata['format'] = img.format
            except ImportError:
                # PIL not available, skip image metadata
                pass
        except Exception as e:
            logger.debug(f"Could not extract image metadata from {file_path}: {e}")
        
        return metadata
    
    def _get_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract video metadata."""
        metadata = {}
        
        try:
            # Try to get video info using ffprobe if available
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(file_path)
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                
                if 'format' in info:
                    metadata['duration'] = float(info['format'].get('duration', 0))
                    metadata['bitrate'] = int(info['format'].get('bit_rate', 0))
                
                # Get video stream info
                for stream in info.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        metadata['width'] = stream.get('width')
                        metadata['height'] = stream.get('height')
                        metadata['codec'] = stream.get('codec_name')
                        break
                        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # ffprobe not available or failed
            pass
        except Exception as e:
            logger.debug(f"Could not extract video metadata from {file_path}: {e}")
        
        return metadata


class GitIntegration:
    """
    Git integration for detecting releases, tags, and version changes.
    
    Monitors Git repository for new releases, tags, and significant
    commits that should trigger project synchronization.
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize Git integration.
        
        Args:
            project_path: Path to the Git repository
        """
        self.project_path = project_path
        self.git_dir = project_path / '.git'
        self.is_git_repo = self.git_dir.exists()
        
        # Track last known state
        self.last_commit_hash: Optional[str] = None
        self.last_tag: Optional[str] = None
        self.known_tags: Set[str] = set()
        
        if self.is_git_repo:
            self._initialize_git_state()
    
    def _initialize_git_state(self) -> None:
        """Initialize Git repository state tracking."""
        try:
            # Get current commit hash
            self.last_commit_hash = self._get_current_commit_hash()
            
            # Get current tags
            self.known_tags = set(self._get_all_tags())
            if self.known_tags:
                self.last_tag = self._get_latest_tag()
                
        except Exception as e:
            logger.warning(f"Failed to initialize Git state: {e}")
    
    def check_for_releases(self) -> List[Dict[str, Any]]:
        """
        Check for new releases and tags.
        
        Returns:
            List of new release information
        """
        if not self.is_git_repo:
            return []
        
        releases = []
        
        try:
            # Check for new tags
            current_tags = set(self._get_all_tags())
            new_tags = current_tags - self.known_tags
            
            for tag in new_tags:
                release_info = self._get_tag_info(tag)
                if release_info:
                    releases.append(release_info)
            
            # Update known tags
            self.known_tags = current_tags
            
            # Check for version file changes
            version_changes = self._check_version_file_changes()
            releases.extend(version_changes)
            
        except Exception as e:
            logger.error(f"Error checking for releases: {e}")
        
        return releases
    
    def _get_current_commit_hash(self) -> Optional[str]:
        """Get current commit hash."""
        try:
            result = subprocess.run([
                'git', 'rev-parse', 'HEAD'
            ], cwd=self.project_path, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Could not get current commit hash: {e}")
        
        return None
    
    def _get_all_tags(self) -> List[str]:
        """Get all Git tags."""
        try:
            result = subprocess.run([
                'git', 'tag', '--sort=-version:refname'
            ], cwd=self.project_path, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return [tag.strip() for tag in result.stdout.split('\n') if tag.strip()]
        except Exception as e:
            logger.debug(f"Could not get Git tags: {e}")
        
        return []
    
    def _get_latest_tag(self) -> Optional[str]:
        """Get the latest Git tag."""
        tags = self._get_all_tags()
        return tags[0] if tags else None
    
    def _get_tag_info(self, tag: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific tag.
        
        Args:
            tag: Tag name
            
        Returns:
            Dictionary with tag information
        """
        try:
            # Get tag commit hash
            result = subprocess.run([
                'git', 'rev-list', '-n', '1', tag
            ], cwd=self.project_path, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return None
            
            commit_hash = result.stdout.strip()
            
            # Get tag message (if annotated tag)
            result = subprocess.run([
                'git', 'tag', '-l', '--format=%(contents)', tag
            ], cwd=self.project_path, capture_output=True, text=True, timeout=10)
            
            tag_message = result.stdout.strip() if result.returncode == 0 else ""
            
            # Get commit message
            result = subprocess.run([
                'git', 'log', '--format=%B', '-n', '1', commit_hash
            ], cwd=self.project_path, capture_output=True, text=True, timeout=10)
            
            commit_message = result.stdout.strip() if result.returncode == 0 else ""
            
            # Get commit date
            result = subprocess.run([
                'git', 'log', '--format=%ci', '-n', '1', commit_hash
            ], cwd=self.project_path, capture_output=True, text=True, timeout=10)
            
            commit_date = result.stdout.strip() if result.returncode == 0 else ""
            
            return {
                'tag': tag,
                'commit_hash': commit_hash,
                'tag_message': tag_message,
                'commit_message': commit_message,
                'commit_date': commit_date,
                'is_release': self._is_release_tag(tag)
            }
            
        except Exception as e:
            logger.warning(f"Error getting tag info for {tag}: {e}")
            return None
    
    def _is_release_tag(self, tag: str) -> bool:
        """Check if tag represents a release."""
        release_patterns = [
            r'^v?\d+\.\d+\.\d+',  # Semantic versioning
            r'^v?\d+\.\d+',       # Major.minor
            r'release',           # Contains 'release'
            r'stable',            # Contains 'stable'
        ]
        
        tag_lower = tag.lower()
        return any(re.search(pattern, tag_lower) for pattern in release_patterns)
    
    def _check_version_file_changes(self) -> List[Dict[str, Any]]:
        """Check for changes in version files."""
        version_files = [
            'VERSION',
            'version.txt',
            'package.json',
            'pyproject.toml',
            'Cargo.toml',
            'pom.xml',
            'setup.py',
            '__version__.py'
        ]
        
        changes = []
        
        for version_file in version_files:
            file_path = self.project_path / version_file
            if file_path.exists():
                version_info = self._extract_version_from_file(file_path)
                if version_info:
                    changes.append({
                        'type': 'version_file_change',
                        'file': version_file,
                        'version': version_info['version'],
                        'previous_version': version_info.get('previous_version'),
                        'is_release': True
                    })
        
        return changes
    
    def _extract_version_from_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract version information from a file."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            if file_path.name == 'package.json':
                import json
                data = json.loads(content)
                return {'version': data.get('version')}
            
            elif file_path.name in ['pyproject.toml', 'Cargo.toml']:
                # Simple TOML parsing for version
                version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    return {'version': version_match.group(1)}
            
            elif file_path.name in ['VERSION', 'version.txt']:
                # Plain text version file
                version = content.strip().split('\n')[0].strip()
                if version:
                    return {'version': version}
            
            elif file_path.name == 'setup.py':
                # Extract version from setup.py
                version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    return {'version': version_match.group(1)}
            
        except Exception as e:
            logger.debug(f"Could not extract version from {file_path}: {e}")
        
        return None
    
    def get_recent_commits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent commits.
        
        Args:
            limit: Maximum number of commits to return
            
        Returns:
            List of commit information
        """
        if not self.is_git_repo:
            return []
        
        commits = []
        
        try:
            result = subprocess.run([
                'git', 'log', f'--max-count={limit}',
                '--format=%H|%s|%an|%ae|%ci'
            ], cwd=self.project_path, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 5:
                            commits.append({
                                'hash': parts[0],
                                'subject': parts[1],
                                'author_name': parts[2],
                                'author_email': parts[3],
                                'date': parts[4]
                            })
            
        except Exception as e:
            logger.error(f"Error getting recent commits: {e}")
        
        return commits


class ProjectFileEventHandler(FileSystemEventHandler):
    """
    File system event handler for watchdog integration.
    """
    
    def __init__(self, monitor: ProjectFileMonitor):
        """
        Initialize event handler.
        
        Args:
            monitor: ProjectFileMonitor instance
        """
        super().__init__()
        self.monitor = monitor
    
    def on_any_event(self, event: FileSystemEvent) -> None:
        """
        Handle any file system event.
        
        Args:
            event: File system event
        """
        if not event.is_directory:  # Only process file events
            self.monitor.handle_file_change(event)