#!/usr/bin/env python3
"""
File Watcher Core - Essential file watching functionality

Extracted from file_watcher.py for RM-DDD compliance.
Single responsibility: Core file system watching and event handling.
"""

import hashlib
import logging
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Callable, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .models import FileChangeEvent, ChangeType, ContentType, DevpostConfig

logger = logging.getLogger(__name__)


class FileWatcherCore:
    """
    Core file system monitoring functionality.
    
    Provides essential file watching capabilities with debouncing
    and event handling infrastructure.
    """
    
    def __init__(
        self,
        project_path: Path,
        config: Optional[DevpostConfig] = None
    ):
        """Initialize core file watcher."""
        self.project_path = Path(project_path).resolve()
        self.config = config or DevpostConfig()
        
        # File tracking
        self.file_hashes: Dict[str, str] = {}
        self.file_timestamps: Dict[str, float] = {}
        self.ignored_patterns: Set[str] = self._get_ignored_patterns()
        
        # Debouncing
        self.debounce_delay = 2.0
        self.pending_changes: Dict[str, FileChangeEvent] = {}
        self.debounce_timer: Optional[threading.Timer] = None
        
        # Event handling
        self.change_callbacks: List[Callable[[FileChangeEvent], None]] = []
        self.event_queue: deque = deque(maxlen=1000)
        
        # Monitoring state
        self.is_monitoring = False
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[ProjectFileEventHandler] = None
        
        # Statistics
        self.stats = {
            'files_monitored': 0,
            'changes_detected': 0,
            'changes_processed': 0,
            'last_scan': None
        }
    
    def _get_ignored_patterns(self) -> Set[str]:
        """Get patterns to ignore during file monitoring."""
        return {
            '*.pyc', '*.pyo', '__pycache__', '.git', '.DS_Store',
            '*.log', '*.tmp', '*.swp', '*.swo', 'node_modules',
            '.venv', 'venv', 'env', '.env', '*.egg-info'
        }
    
    def add_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Add callback for file change events."""
        self.change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Remove callback for file change events."""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
    
    def start_monitoring(self) -> bool:
        """Start file system monitoring."""
        if self.is_monitoring:
            logger.warning("File monitoring already active")
            return False
        
        try:
            self.event_handler = ProjectFileEventHandler(self)
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                str(self.project_path),
                recursive=True
            )
            self.observer.start()
            self.is_monitoring = True
            self._perform_initial_scan()
            logger.info(f"Started monitoring {self.project_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop file system monitoring."""
        if not self.is_monitoring:
            return False
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None
            
            if self.debounce_timer:
                self.debounce_timer.cancel()
                self.debounce_timer = None
            
            self.is_monitoring = False
            logger.info("Stopped file monitoring")
            return True
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return False
    
    def _perform_initial_scan(self) -> None:
        """Perform initial scan of project files."""
        logger.info("Performing initial file scan...")
        
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                self._track_file(file_path)
        
        self.stats['files_monitored'] = len(self.file_hashes)
        self.stats['last_scan'] = datetime.now()
        logger.info(f"Initial scan complete: {self.stats['files_monitored']} files tracked")
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        for pattern in self.ignored_patterns:
            if file_path.match(pattern) or pattern in str(file_path):
                return True
        return False
    
    def _track_file(self, file_path: Path) -> None:
        """Track file for changes."""
        try:
            file_str = str(file_path)
            stat = file_path.stat()
            self.file_timestamps[file_str] = stat.st_mtime
            
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    file_hash = hashlib.md5(content).hexdigest()
                    self.file_hashes[file_str] = file_hash
            except (IOError, OSError):
                pass
                
        except Exception as e:
            logger.debug(f"Error tracking file {file_path}: {e}")
    
    def _handle_file_change(self, file_path: Path, change_type: ChangeType) -> None:
        """Handle file change event."""
        if self._should_ignore_file(file_path):
            return
        
        file_str = str(file_path)
        event = FileChangeEvent(
            file_path=file_path,
            change_type=change_type,
            timestamp=datetime.now(),
            content_type=self._detect_content_type(file_path)
        )
        
        self.pending_changes[file_str] = event
        self.stats['changes_detected'] += 1
        self._start_debounce_timer()
    
    def _detect_content_type(self, file_path: Path) -> ContentType:
        """Detect content type of file."""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.py']:
            return ContentType.CODE
        elif suffix in ['.md', '.txt', '.rst']:
            return ContentType.DOCUMENTATION
        elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
            return ContentType.IMAGE
        elif suffix in ['.mp4', '.avi', '.mov', '.webm']:
            return ContentType.VIDEO
        elif suffix in ['.zip', '.tar', '.gz']:
            return ContentType.ARCHIVE
        else:
            return ContentType.OTHER
    
    def _start_debounce_timer(self) -> None:
        """Start debounce timer for processing changes."""
        if self.debounce_timer:
            self.debounce_timer.cancel()
        
        self.debounce_timer = threading.Timer(
            self.debounce_delay,
            self._process_pending_changes
        )
        self.debounce_timer.start()
    
    def _process_pending_changes(self) -> None:
        """Process all pending file changes."""
        if not self.pending_changes:
            return
        
        logger.info(f"Processing {len(self.pending_changes)} pending changes")
        
        for event in self.pending_changes.values():
            self._notify_change_callbacks(event)
            self.stats['changes_processed'] += 1
        
        self.pending_changes.clear()
        self._update_file_tracking()
    
    def _notify_change_callbacks(self, event: FileChangeEvent) -> None:
        """Notify all registered callbacks of file change."""
        for callback in self.change_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in change callback: {e}")
    
    def _update_file_tracking(self) -> None:
        """Update file tracking information."""
        for file_path in list(self.file_hashes.keys()):
            path = Path(file_path)
            if not path.exists():
                del self.file_hashes[file_path]
                if file_path in self.file_timestamps:
                    del self.file_timestamps[file_path]
            else:
                self._track_file(path)
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            **self.stats,
            'is_monitoring': self.is_monitoring,
            'pending_changes': len(self.pending_changes),
            'files_tracked': len(self.file_hashes)
        }


class ProjectFileEventHandler(FileSystemEventHandler):
    """File system event handler for project monitoring."""
    
    def __init__(self, watcher: FileWatcherCore):
        """Initialize event handler."""
        self.watcher = watcher
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification event."""
        if not event.is_directory:
            self.watcher._handle_file_change(
                Path(event.src_path),
                ChangeType.MODIFIED
            )
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation event."""
        if not event.is_directory:
            self.watcher._handle_file_change(
                Path(event.src_path),
                ChangeType.CREATED
            )
    
    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion event."""
        if not event.is_directory:
            self.watcher._handle_file_change(
                Path(event.src_path),
                ChangeType.DELETED
            )
    
    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file move event."""
        if not event.is_directory:
            self.watcher._handle_file_change(
                Path(event.src_path),
                ChangeType.DELETED
            )
            self.watcher._handle_file_change(
                Path(event.dest_path),
                ChangeType.CREATED
            )
