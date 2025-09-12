"""
File Monitor Core Core Core

This module was extracted from file_monitor_core_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
import threading
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import List, Dict, Set, Optional, Callable, Any
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from ..interfaces import FileMonitorInterface, SyncManagerInterface
from ..models import FileChangeEvent, ChangeType, DevpostConfig
from .content_analyzer import ContentAnalyzer
from ....utils.path_normalizer import safe_relative_to
import fnmatch
import fnmatch
from ..models import SyncOperation, SyncOperationType
import fnmatch
import fnmatch
import fnmatch
import fnmatch
from ..models import SyncOperation, SyncOperationType
import fnmatch
import fnmatch
import fnmatch
import fnmatch
import fnmatch
import fnmatch
from ..models import SyncOperation, SyncOperationType

class ProjectFileMonitor(FileMonitorInterface):
    """
    Monitors project files for changes and triggers sync operations.
    
    This class implements file system watching using the watchdog library,
    with configurable file pattern matching, change event filtering,
    and debouncing logic to prevent excessive sync operations.
    """

    def __init__(self, project_path: Path, config: DevpostConfig, sync_manager: Optional[SyncManagerInterface]=None, debounce_delay: float=2.0, max_queue_size: int=1000):
        """
        Initialize the file monitor.
        
        Args:
            project_path: Path to the project directory to monitor
            config: Devpost configuration with watch patterns
            sync_manager: Optional sync manager for triggering operations
            debounce_delay: Delay in seconds before processing changes
            max_queue_size: Maximum number of events to queue
        """
        self.project_path = Path(project_path).resolve()
        self.config = config
        self.sync_manager = sync_manager
        self.debounce_delay = debounce_delay
        self.max_queue_size = max_queue_size
        self.content_analyzer = ContentAnalyzer(self.project_path)
        self._observer: Optional[Observer] = None
        self._event_handler: Optional[DevpostFileEventHandler] = None
        self._is_monitoring = False
        self._lock = threading.RLock()
        self._event_queue: deque = deque(maxlen=max_queue_size)
        self._debounce_timers: Dict[str, threading.Timer] = {}
        self._recent_changes: Dict[str, FileChangeEvent] = {}
        self._processing_thread: Optional[threading.Thread] = None
        self._stop_processing = threading.Event()
        self._watch_paths: Set[Path] = set()
        self._excluded_patterns = {'*.pyc', '__pycache__', '.git', '.DS_Store', '*.tmp', '*.swp', '*.log', 'node_modules'}
        self._change_callbacks: List[Callable[[FileChangeEvent], None]] = []
        logger.info(f'Initialized file monitor for {self.project_path}')

    def start_monitoring(self) -> None:
        """Start monitoring project files for changes."""
        with self._lock:
            if self._is_monitoring:
                logger.warning('File monitoring is already active')
                return
            try:
                self._observer = Observer()
                self._event_handler = DevpostFileEventHandler(self)
                self.add_watch_path(self.project_path)
                self._observer.start()
                self._stop_processing.clear()
                self._processing_thread = threading.Thread(target=self._process_events, daemon=True, name='DevpostFileMonitor')
                self._processing_thread.start()
                self._is_monitoring = True
                logger.info('File monitoring started successfully')
            except Exception as e:
                logger.error(f'Failed to start file monitoring: {e}')
                self._cleanup()
                raise

    def stop_monitoring(self) -> None:
        """Stop file monitoring with proper cleanup to prevent deadlocks."""
        if not self._is_monitoring:
            return
        logger.info('Stopping file monitoring...')
        try:
            self._stop_processing.set()
            if self._observer:
                try:
                    self._observer.stop()
                    self._observer.join(timeout=2.0)
                    if self._observer.is_alive():
                        logger.warning('Observer thread did not stop gracefully')
                except Exception as e:
                    logger.warning(f'Error stopping observer: {e}')
                finally:
                    self._observer = None
            if self._processing_thread and self._processing_thread.is_alive():
                try:
                    self._processing_thread.join(timeout=2.0)
                    if self._processing_thread.is_alive():
                        logger.warning('Processing thread did not stop gracefully')
                except Exception as e:
                    logger.warning(f'Error stopping processing thread: {e}')
            timers_to_cancel = list(self._debounce_timers.values())
            self._debounce_timers.clear()
            for timer in timers_to_cancel:
                try:
                    timer.cancel()
                except Exception as e:
                    logger.warning(f'Error canceling timer: {e}')
            with self._lock:
                self._cleanup()
            logger.info('File monitoring stopped')
        except Exception as e:
            logger.error(f'Error stopping file monitoring: {e}')
            try:
                with self._lock:
                    self._cleanup()
            except Exception as cleanup_error:
                logger.error(f'Error during cleanup: {cleanup_error}')

    def add_watch_path(self, path: Path) -> None:
        """Add a path to be monitored."""
        path = Path(path).resolve()
        if not path.exists():
            logger.warning(f'Watch path does not exist: {path}')
            return
        if not path.is_dir():
            logger.warning(f'Watch path is not a directory: {path}')
            return
        with self._lock:
            if path in self._watch_paths:
                return
            self._watch_paths.add(path)
            if self._observer and self._event_handler:
                try:
                    self._observer.schedule(self._event_handler, str(path), recursive=True)
                    logger.debug(f'Added watch path: {path}')
                except Exception as e:
                    logger.error(f'Failed to add watch path {path}: {e}')
                    self._watch_paths.discard(path)

    def remove_watch_path(self, path: Path) -> None:
        """Remove a path from monitoring."""
        path = Path(path).resolve()
        with self._lock:
            if path not in self._watch_paths:
                return
            self._watch_paths.discard(path)
            logger.debug(f'Removed watch path: {path}')

    def get_recent_changes(self, since: Optional[datetime]=None) -> List[FileChangeEvent]:
        """Get recent file changes."""
        if since is None:
            since = datetime.now() - timedelta(hours=1)
        with self._lock:
            return [event for event in self._recent_changes.values() if event.timestamp >= since]

    def add_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Add callback to be called when changes are detected."""
        self._change_callbacks.append(callback)

    def remove_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Remove change callback."""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)

    def _handle_file_event(self, file_path: str, change_type: ChangeType) -> None:
        """Handle a file system event with deadlock prevention."""
        try:
            if self._stop_processing.is_set():
                return
            path = Path(file_path)
            if not self._is_relevant_file(path):
                return
            event = self._create_change_event(path, change_type)
            if not event:
                return
            try:
                with self._lock:
                    if not self._stop_processing.is_set():
                        self._event_queue.append(event)
                    else:
                        return
            except Exception as lock_error:
                logger.warning(f'Could not acquire lock for file event {file_path}: {lock_error}')
                return
            self._schedule_debounced_processing(str(path))
        except Exception as e:
            logger.error(f'Error handling file event for {file_path}: {e}')

    def _is_relevant_file(self, path: Path) -> bool:
        """Check if file is relevant for monitoring."""
        try:
            path = path.resolve()
            if not str(path).startswith(str(self.project_path)):
                return False
            import fnmatch
            filename = path.name
            for pattern in self._excluded_patterns:
                if fnmatch.fnmatch(filename, pattern):
                    return False
            for parent in path.parents:
                if parent.name in {'__pycache__', '.git', 'node_modules'}:
                    return False
            return True
        except Exception as e:
            logger.error(f'Error checking file relevance for {path}: {e}')
            return False

    def _create_change_event(self, path: Path, change_type: ChangeType) -> Optional[FileChangeEvent]:
        """Create a FileChangeEvent from path and change type."""
        try:
            file_size = None
            if change_type != ChangeType.DELETED and path.exists():
                try:
                    file_size = path.stat().st_size
                except OSError:
                    pass
            affects_sync = self._should_trigger_sync(path)
            analysis = self.content_analyzer.analyze_file_change(path, change_type.value)
            event = FileChangeEvent(file_path=path, change_type=change_type, timestamp=datetime.now(), affects_sync=affects_sync, file_size=file_size, content_hash=analysis.get('content_hash'), previous_content_hash=analysis.get('previous_content_hash'), is_significant_change=analysis.get('is_significant_change', True), media_metadata=analysis.get('media_metadata'), git_info=analysis.get('git_info'), content_type=analysis.get('content_type'))
            return event
        except Exception as e:
            logger.error(f'Error creating change event for {path}: {e}')
            return None

    def _should_trigger_sync(self, path: Path) -> bool:
        """Check if file change should trigger sync."""
        import fnmatch
        filename = path.name
        relative_path_obj = safe_relative_to(path, self.project_path)
        if relative_path_obj is None:
            return False
        relative_path = str(relative_path_obj)
        for pattern in self.config.watch_patterns:
            if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(relative_path, pattern):
                return True
        return False

    def _schedule_debounced_processing(self, file_path: str) -> None:
        """Schedule debounced processing for a file."""
        with self._lock:
            if file_path in self._debounce_timers:
                self._debounce_timers[file_path].cancel()
            timer = threading.Timer(self.debounce_delay, self._process_debounced_file, args=[file_path])
            self._debounce_timers[file_path] = timer
            timer.start()

    def _process_debounced_file(self, file_path: str) -> None:
        """Process changes for a specific file after debounce delay."""
        with self._lock:
            self._debounce_timers.pop(file_path, None)
            latest_event = None
            for event in reversed(self._event_queue):
                if str(event.file_path) == file_path:
                    latest_event = event
                    break
            if latest_event:
                self._process_change_event(latest_event)

    def _process_events(self) -> None:
        """Background thread for processing file change events."""
        logger.debug('Event processing thread started')
        while not self._stop_processing.is_set():
            try:
                events_to_process = []
                with self._lock:
                    current_time = datetime.now()
                    while self._event_queue:
                        event = self._event_queue[0]
                        if (current_time - event.timestamp).total_seconds() >= self.debounce_delay:
                            events_to_process.append(self._event_queue.popleft())
                        else:
                            break
                for event in events_to_process:
                    self._process_change_event(event)
                time.sleep(0.1)
            except Exception as e:
                logger.error(f'Error in event processing thread: {e}')
                time.sleep(1.0)
        logger.debug('Event processing thread stopped')

    def _process_change_event(self, event: FileChangeEvent) -> None:
        """Process a single change event."""
        try:
            with self._lock:
                self._recent_changes[str(event.file_path)] = event
                if len(self._recent_changes) > 1000:
                    sorted_events = sorted(self._recent_changes.items(), key=lambda x: x[1].timestamp)
                    for path, _ in sorted_events[:100]:
                        self._recent_changes.pop(path, None)
            logger.debug(f'Processing change: {event.change_type} {event.file_path}')
            for callback in self._change_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f'Error in change callback: {e}')
            if event.affects_sync and self.sync_manager:
                try:
                    from ..models import SyncOperation, SyncOperationType
                    if event.is_documentation_file():
                        operation_type = SyncOperationType.DOCUMENTATION_UPDATE
                    elif event.is_media_file():
                        operation_type = SyncOperationType.MEDIA_UPLOAD
                    else:
                        operation_type = SyncOperationType.METADATA_UPDATE
                    relative_path = safe_relative_to(event.file_path, self.project_path)
                    if relative_path is not None:
                        target_field = str(relative_path)
                    else:
                        target_field = Path(event.file_path).name
                    sync_op = SyncOperation(operation_type=operation_type, target_field=target_field, local_value=str(event.file_path), priority=3 if event.is_media_file() else 5)
                    self.sync_manager.queue_sync_operation(sync_op)
                    logger.debug(f'Queued sync operation for {event.file_path}')
                except Exception as e:
                    logger.error(f'Error queuing sync operation: {e}')
        except Exception as e:
            logger.error(f'Error processing change event: {e}')

    def _cleanup(self) -> None:
        """Clean up resources."""
        self._is_monitoring = False
        self._observer = None
        self._event_handler = None
        self._processing_thread = None
        self._watch_paths.clear()
        self._event_queue.clear()
        self._recent_changes.clear()

    def __enter__(self):
        """Context manager entry."""
        self.start_monitoring()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_monitoring()

def __init__(self, monitor: 'ProjectFileMonitor'):
    super().__init__()
    self.monitor = monitor

def on_created(self, event: FileSystemEvent) -> None:
    """Handle file creation events."""
    if not event.is_directory:
        self.monitor._handle_file_event(event.src_path, ChangeType.CREATED)

def on_modified(self, event: FileSystemEvent) -> None:
    """Handle file modification events."""
    if not event.is_directory:
        self.monitor._handle_file_event(event.src_path, ChangeType.MODIFIED)

def on_deleted(self, event: FileSystemEvent) -> None:
    """Handle file deletion events."""
    if not event.is_directory:
        self.monitor._handle_file_event(event.src_path, ChangeType.DELETED)

def on_moved(self, event: FileSystemEvent) -> None:
    """Handle file move events."""
    if not event.is_directory and hasattr(event, 'dest_path'):
        self.monitor._handle_file_event(event.src_path, ChangeType.DELETED)
        self.monitor._handle_file_event(event.dest_path, ChangeType.CREATED)

def __init__(self, project_path: Path, config: DevpostConfig, sync_manager: Optional[SyncManagerInterface]=None, debounce_delay: float=2.0, max_queue_size: int=1000):
    """
        Initialize the file monitor.
        
        Args:
            project_path: Path to the project directory to monitor
            config: Devpost configuration with watch patterns
            sync_manager: Optional sync manager for triggering operations
            debounce_delay: Delay in seconds before processing changes
            max_queue_size: Maximum number of events to queue
        """
    self.project_path = Path(project_path).resolve()
    self.config = config
    self.sync_manager = sync_manager
    self.debounce_delay = debounce_delay
    self.max_queue_size = max_queue_size
    self.content_analyzer = ContentAnalyzer(self.project_path)
    self._observer: Optional[Observer] = None
    self._event_handler: Optional[DevpostFileEventHandler] = None
    self._is_monitoring = False
    self._lock = threading.RLock()
    self._event_queue: deque = deque(maxlen=max_queue_size)
    self._debounce_timers: Dict[str, threading.Timer] = {}
    self._recent_changes: Dict[str, FileChangeEvent] = {}
    self._processing_thread: Optional[threading.Thread] = None
    self._stop_processing = threading.Event()
    self._watch_paths: Set[Path] = set()
    self._excluded_patterns = {'*.pyc', '__pycache__', '.git', '.DS_Store', '*.tmp', '*.swp', '*.log', 'node_modules'}
    self._change_callbacks: List[Callable[[FileChangeEvent], None]] = []
    logger.info(f'Initialized file monitor for {self.project_path}')

def start_monitoring(self) -> None:
    """Start monitoring project files for changes."""
    with self._lock:
        if self._is_monitoring:
            logger.warning('File monitoring is already active')
            return
        try:
            self._observer = Observer()
            self._event_handler = DevpostFileEventHandler(self)
            self.add_watch_path(self.project_path)
            self._observer.start()
            self._stop_processing.clear()
            self._processing_thread = threading.Thread(target=self._process_events, daemon=True, name='DevpostFileMonitor')
            self._processing_thread.start()
            self._is_monitoring = True
            logger.info('File monitoring started successfully')
        except Exception as e:
            logger.error(f'Failed to start file monitoring: {e}')
            self._cleanup()
            raise

def stop_monitoring(self) -> None:
    """Stop file monitoring with proper cleanup to prevent deadlocks."""
    if not self._is_monitoring:
        return
    logger.info('Stopping file monitoring...')
    try:
        self._stop_processing.set()
        if self._observer:
            try:
                self._observer.stop()
                self._observer.join(timeout=2.0)
                if self._observer.is_alive():
                    logger.warning('Observer thread did not stop gracefully')
            except Exception as e:
                logger.warning(f'Error stopping observer: {e}')
            finally:
                self._observer = None
        if self._processing_thread and self._processing_thread.is_alive():
            try:
                self._processing_thread.join(timeout=2.0)
                if self._processing_thread.is_alive():
                    logger.warning('Processing thread did not stop gracefully')
            except Exception as e:
                logger.warning(f'Error stopping processing thread: {e}')
        timers_to_cancel = list(self._debounce_timers.values())
        self._debounce_timers.clear()
        for timer in timers_to_cancel:
            try:
                timer.cancel()
            except Exception as e:
                logger.warning(f'Error canceling timer: {e}')
        with self._lock:
            self._cleanup()
        logger.info('File monitoring stopped')
    except Exception as e:
        logger.error(f'Error stopping file monitoring: {e}')
        try:
            with self._lock:
                self._cleanup()
        except Exception as cleanup_error:
            logger.error(f'Error during cleanup: {cleanup_error}')

def add_watch_path(self, path: Path) -> None:
    """Add a path to be monitored."""
    path = Path(path).resolve()
    if not path.exists():
        logger.warning(f'Watch path does not exist: {path}')
        return
    if not path.is_dir():
        logger.warning(f'Watch path is not a directory: {path}')
        return
    with self._lock:
        if path in self._watch_paths:
            return
        self._watch_paths.add(path)
        if self._observer and self._event_handler:
            try:
                self._observer.schedule(self._event_handler, str(path), recursive=True)
                logger.debug(f'Added watch path: {path}')
            except Exception as e:
                logger.error(f'Failed to add watch path {path}: {e}')
                self._watch_paths.discard(path)

def remove_watch_path(self, path: Path) -> None:
    """Remove a path from monitoring."""
    path = Path(path).resolve()
    with self._lock:
        if path not in self._watch_paths:
            return
        self._watch_paths.discard(path)
        logger.debug(f'Removed watch path: {path}')

def get_recent_changes(self, since: Optional[datetime]=None) -> List[FileChangeEvent]:
    """Get recent file changes."""
    if since is None:
        since = datetime.now() - timedelta(hours=1)
    with self._lock:
        return [event for event in self._recent_changes.values() if event.timestamp >= since]

def add_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
    """Add callback to be called when changes are detected."""
    self._change_callbacks.append(callback)

def remove_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
    """Remove change callback."""
    if callback in self._change_callbacks:
        self._change_callbacks.remove(callback)

def _handle_file_event(self, file_path: str, change_type: ChangeType) -> None:
    """Handle a file system event with deadlock prevention."""
    try:
        if self._stop_processing.is_set():
            return
        path = Path(file_path)
        if not self._is_relevant_file(path):
            return
        event = self._create_change_event(path, change_type)
        if not event:
            return
        try:
            with self._lock:
                if not self._stop_processing.is_set():
                    self._event_queue.append(event)
                else:
                    return
        except Exception as lock_error:
            logger.warning(f'Could not acquire lock for file event {file_path}: {lock_error}')
            return
        self._schedule_debounced_processing(str(path))
    except Exception as e:
        logger.error(f'Error handling file event for {file_path}: {e}')

def _is_relevant_file(self, path: Path) -> bool:
    """Check if file is relevant for monitoring."""
    try:
        path = path.resolve()
        if not str(path).startswith(str(self.project_path)):
            return False
        import fnmatch
        filename = path.name
        for pattern in self._excluded_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return False
        for parent in path.parents:
            if parent.name in {'__pycache__', '.git', 'node_modules'}:
                return False
        return True
    except Exception as e:
        logger.error(f'Error checking file relevance for {path}: {e}')
        return False

def _create_change_event(self, path: Path, change_type: ChangeType) -> Optional[FileChangeEvent]:
    """Create a FileChangeEvent from path and change type."""
    try:
        file_size = None
        if change_type != ChangeType.DELETED and path.exists():
            try:
                file_size = path.stat().st_size
            except OSError:
                pass
        affects_sync = self._should_trigger_sync(path)
        analysis = self.content_analyzer.analyze_file_change(path, change_type.value)
        event = FileChangeEvent(file_path=path, change_type=change_type, timestamp=datetime.now(), affects_sync=affects_sync, file_size=file_size, content_hash=analysis.get('content_hash'), previous_content_hash=analysis.get('previous_content_hash'), is_significant_change=analysis.get('is_significant_change', True), media_metadata=analysis.get('media_metadata'), git_info=analysis.get('git_info'), content_type=analysis.get('content_type'))
        return event
    except Exception as e:
        logger.error(f'Error creating change event for {path}: {e}')
        return None

def _should_trigger_sync(self, path: Path) -> bool:
    """Check if file change should trigger sync."""
    import fnmatch
    filename = path.name
    relative_path_obj = safe_relative_to(path, self.project_path)
    if relative_path_obj is None:
        return False
    relative_path = str(relative_path_obj)
    for pattern in self.config.watch_patterns:
        if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(relative_path, pattern):
            return True
    return False

def _cleanup(self) -> None:
    """Clean up resources."""
    self._is_monitoring = False
    self._observer = None
    self._event_handler = None
    self._processing_thread = None
    self._watch_paths.clear()
    self._event_queue.clear()
    self._recent_changes.clear()

def __enter__(self):
    """Context manager entry."""
    self.start_monitoring()
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit."""
    self.stop_monitoring()

def __init__(self, project_path: Path, config: DevpostConfig, sync_manager: Optional[SyncManagerInterface]=None, debounce_delay: float=2.0, max_queue_size: int=1000):
    """
        Initialize the file monitor.
        
        Args:
            project_path: Path to the project directory to monitor
            config: Devpost configuration with watch patterns
            sync_manager: Optional sync manager for triggering operations
            debounce_delay: Delay in seconds before processing changes
            max_queue_size: Maximum number of events to queue
        """
    self.project_path = Path(project_path).resolve()
    self.config = config
    self.sync_manager = sync_manager
    self.debounce_delay = debounce_delay
    self.max_queue_size = max_queue_size
    self.content_analyzer = ContentAnalyzer(self.project_path)
    self._observer: Optional[Observer] = None
    self._event_handler: Optional[DevpostFileEventHandler] = None
    self._is_monitoring = False
    self._lock = threading.RLock()
    self._event_queue: deque = deque(maxlen=max_queue_size)
    self._debounce_timers: Dict[str, threading.Timer] = {}
    self._recent_changes: Dict[str, FileChangeEvent] = {}
    self._processing_thread: Optional[threading.Thread] = None
    self._stop_processing = threading.Event()
    self._watch_paths: Set[Path] = set()
    self._excluded_patterns = {'*.pyc', '__pycache__', '.git', '.DS_Store', '*.tmp', '*.swp', '*.log', 'node_modules'}
    self._change_callbacks: List[Callable[[FileChangeEvent], None]] = []
    logger.info(f'Initialized file monitor for {self.project_path}')

def start_monitoring(self) -> None:
    """Start monitoring project files for changes."""
    with self._lock:
        if self._is_monitoring:
            logger.warning('File monitoring is already active')
            return
        try:
            self._observer = Observer()
            self._event_handler = DevpostFileEventHandler(self)
            self.add_watch_path(self.project_path)
            self._observer.start()
            self._stop_processing.clear()
            self._processing_thread = threading.Thread(target=self._process_events, daemon=True, name='DevpostFileMonitor')
            self._processing_thread.start()
            self._is_monitoring = True
            logger.info('File monitoring started successfully')
        except Exception as e:
            logger.error(f'Failed to start file monitoring: {e}')
            self._cleanup()
            raise

def stop_monitoring(self) -> None:
    """Stop file monitoring with proper cleanup to prevent deadlocks."""
    if not self._is_monitoring:
        return
    logger.info('Stopping file monitoring...')
    try:
        self._stop_processing.set()
        if self._observer:
            try:
                self._observer.stop()
                self._observer.join(timeout=2.0)
                if self._observer.is_alive():
                    logger.warning('Observer thread did not stop gracefully')
            except Exception as e:
                logger.warning(f'Error stopping observer: {e}')
            finally:
                self._observer = None
        if self._processing_thread and self._processing_thread.is_alive():
            try:
                self._processing_thread.join(timeout=2.0)
                if self._processing_thread.is_alive():
                    logger.warning('Processing thread did not stop gracefully')
            except Exception as e:
                logger.warning(f'Error stopping processing thread: {e}')
        timers_to_cancel = list(self._debounce_timers.values())
        self._debounce_timers.clear()
        for timer in timers_to_cancel:
            try:
                timer.cancel()
            except Exception as e:
                logger.warning(f'Error canceling timer: {e}')
        with self._lock:
            self._cleanup()
        logger.info('File monitoring stopped')
    except Exception as e:
        logger.error(f'Error stopping file monitoring: {e}')
        try:
            with self._lock:
                self._cleanup()
        except Exception as cleanup_error:
            logger.error(f'Error during cleanup: {cleanup_error}')

def add_watch_path(self, path: Path) -> None:
    """Add a path to be monitored."""
    path = Path(path).resolve()
    if not path.exists():
        logger.warning(f'Watch path does not exist: {path}')
        return
    if not path.is_dir():
        logger.warning(f'Watch path is not a directory: {path}')
        return
    with self._lock:
        if path in self._watch_paths:
            return
        self._watch_paths.add(path)
        if self._observer and self._event_handler:
            try:
                self._observer.schedule(self._event_handler, str(path), recursive=True)
                logger.debug(f'Added watch path: {path}')
            except Exception as e:
                logger.error(f'Failed to add watch path {path}: {e}')
                self._watch_paths.discard(path)

def remove_watch_path(self, path: Path) -> None:
    """Remove a path from monitoring."""
    path = Path(path).resolve()
    with self._lock:
        if path not in self._watch_paths:
            return
        self._watch_paths.discard(path)
        logger.debug(f'Removed watch path: {path}')

def get_recent_changes(self, since: Optional[datetime]=None) -> List[FileChangeEvent]:
    """Get recent file changes."""
    if since is None:
        since = datetime.now() - timedelta(hours=1)
    with self._lock:
        return [event for event in self._recent_changes.values() if event.timestamp >= since]

def add_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
    """Add callback to be called when changes are detected."""
    self._change_callbacks.append(callback)

def remove_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
    """Remove change callback."""
    if callback in self._change_callbacks:
        self._change_callbacks.remove(callback)

def _handle_file_event(self, file_path: str, change_type: ChangeType) -> None:
    """Handle a file system event with deadlock prevention."""
    try:
        if self._stop_processing.is_set():
            return
        path = Path(file_path)
        if not self._is_relevant_file(path):
            return
        event = self._create_change_event(path, change_type)
        if not event:
            return
        try:
            with self._lock:
                if not self._stop_processing.is_set():
                    self._event_queue.append(event)
                else:
                    return
        except Exception as lock_error:
            logger.warning(f'Could not acquire lock for file event {file_path}: {lock_error}')
            return
        self._schedule_debounced_processing(str(path))
    except Exception as e:
        logger.error(f'Error handling file event for {file_path}: {e}')

def _is_relevant_file(self, path: Path) -> bool:
    """Check if file is relevant for monitoring."""
    try:
        path = path.resolve()
        if not str(path).startswith(str(self.project_path)):
            return False
        import fnmatch
        filename = path.name
        for pattern in self._excluded_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return False
        for parent in path.parents:
            if parent.name in {'__pycache__', '.git', 'node_modules'}:
                return False
        return True
    except Exception as e:
        logger.error(f'Error checking file relevance for {path}: {e}')
        return False

def _create_change_event(self, path: Path, change_type: ChangeType) -> Optional[FileChangeEvent]:
    """Create a FileChangeEvent from path and change type."""
    try:
        file_size = None
        if change_type != ChangeType.DELETED and path.exists():
            try:
                file_size = path.stat().st_size
            except OSError:
                pass
        affects_sync = self._should_trigger_sync(path)
        analysis = self.content_analyzer.analyze_file_change(path, change_type.value)
        event = FileChangeEvent(file_path=path, change_type=change_type, timestamp=datetime.now(), affects_sync=affects_sync, file_size=file_size, content_hash=analysis.get('content_hash'), previous_content_hash=analysis.get('previous_content_hash'), is_significant_change=analysis.get('is_significant_change', True), media_metadata=analysis.get('media_metadata'), git_info=analysis.get('git_info'), content_type=analysis.get('content_type'))
        return event
    except Exception as e:
        logger.error(f'Error creating change event for {path}: {e}')
        return None

def _should_trigger_sync(self, path: Path) -> bool:
    """Check if file change should trigger sync."""
    import fnmatch
    filename = path.name
    relative_path_obj = safe_relative_to(path, self.project_path)
    if relative_path_obj is None:
        return False
    relative_path = str(relative_path_obj)
    for pattern in self.config.watch_patterns:
        if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(relative_path, pattern):
            return True
    return False

def _cleanup(self) -> None:
    """Clean up resources."""
    self._is_monitoring = False
    self._observer = None
    self._event_handler = None
    self._processing_thread = None
    self._watch_paths.clear()
    self._event_queue.clear()
    self._recent_changes.clear()

def __enter__(self):
    """Context manager entry."""
    self.start_monitoring()
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit."""
    self.stop_monitoring()

def __init__(self, project_path: Path, config: DevpostConfig, sync_manager: Optional[SyncManagerInterface]=None, debounce_delay: float=2.0, max_queue_size: int=1000):
    """
        Initialize the file monitor.
        
        Args:
            project_path: Path to the project directory to monitor
            config: Devpost configuration with watch patterns
            sync_manager: Optional sync manager for triggering operations
            debounce_delay: Delay in seconds before processing changes
            max_queue_size: Maximum number of events to queue
        """
    self.project_path = Path(project_path).resolve()
    self.config = config
    self.sync_manager = sync_manager
    self.debounce_delay = debounce_delay
    self.max_queue_size = max_queue_size
    self.content_analyzer = ContentAnalyzer(self.project_path)
    self._observer: Optional[Observer] = None
    self._event_handler: Optional[DevpostFileEventHandler] = None
    self._is_monitoring = False
    self._lock = threading.RLock()
    self._event_queue: deque = deque(maxlen=max_queue_size)
    self._debounce_timers: Dict[str, threading.Timer] = {}
    self._recent_changes: Dict[str, FileChangeEvent] = {}
    self._processing_thread: Optional[threading.Thread] = None
    self._stop_processing = threading.Event()
    self._watch_paths: Set[Path] = set()
    self._excluded_patterns = {'*.pyc', '__pycache__', '.git', '.DS_Store', '*.tmp', '*.swp', '*.log', 'node_modules'}
    self._change_callbacks: List[Callable[[FileChangeEvent], None]] = []
    logger.info(f'Initialized file monitor for {self.project_path}')

def start_monitoring(self) -> None:
    """Start monitoring project files for changes."""
    with self._lock:
        if self._is_monitoring:
            logger.warning('File monitoring is already active')
            return
        try:
            self._observer = Observer()
            self._event_handler = DevpostFileEventHandler(self)
            self.add_watch_path(self.project_path)
            self._observer.start()
            self._stop_processing.clear()
            self._processing_thread = threading.Thread(target=self._process_events, daemon=True, name='DevpostFileMonitor')
            self._processing_thread.start()
            self._is_monitoring = True
            logger.info('File monitoring started successfully')
        except Exception as e:
            logger.error(f'Failed to start file monitoring: {e}')
            self._cleanup()
            raise

def stop_monitoring(self) -> None:
    """Stop file monitoring with proper cleanup to prevent deadlocks."""
    if not self._is_monitoring:
        return
    logger.info('Stopping file monitoring...')
    try:
        self._stop_processing.set()
        if self._observer:
            try:
                self._observer.stop()
                self._observer.join(timeout=2.0)
                if self._observer.is_alive():
                    logger.warning('Observer thread did not stop gracefully')
            except Exception as e:
                logger.warning(f'Error stopping observer: {e}')
            finally:
                self._observer = None
        if self._processing_thread and self._processing_thread.is_alive():
            try:
                self._processing_thread.join(timeout=2.0)
                if self._processing_thread.is_alive():
                    logger.warning('Processing thread did not stop gracefully')
            except Exception as e:
                logger.warning(f'Error stopping processing thread: {e}')
        timers_to_cancel = list(self._debounce_timers.values())
        self._debounce_timers.clear()
        for timer in timers_to_cancel:
            try:
                timer.cancel()
            except Exception as e:
                logger.warning(f'Error canceling timer: {e}')
        with self._lock:
            self._cleanup()
        logger.info('File monitoring stopped')
    except Exception as e:
        logger.error(f'Error stopping file monitoring: {e}')
        try:
            with self._lock:
                self._cleanup()
        except Exception as cleanup_error:
            logger.error(f'Error during cleanup: {cleanup_error}')

def add_watch_path(self, path: Path) -> None:
    """Add a path to be monitored."""
    path = Path(path).resolve()
    if not path.exists():
        logger.warning(f'Watch path does not exist: {path}')
        return
    if not path.is_dir():
        logger.warning(f'Watch path is not a directory: {path}')
        return
    with self._lock:
        if path in self._watch_paths:
            return
        self._watch_paths.add(path)
        if self._observer and self._event_handler:
            try:
                self._observer.schedule(self._event_handler, str(path), recursive=True)
                logger.debug(f'Added watch path: {path}')
            except Exception as e:
                logger.error(f'Failed to add watch path {path}: {e}')
                self._watch_paths.discard(path)

def remove_watch_path(self, path: Path) -> None:
    """Remove a path from monitoring."""
    path = Path(path).resolve()
    with self._lock:
        if path not in self._watch_paths:
            return
        self._watch_paths.discard(path)
        logger.debug(f'Removed watch path: {path}')

def get_recent_changes(self, since: Optional[datetime]=None) -> List[FileChangeEvent]:
    """Get recent file changes."""
    if since is None:
        since = datetime.now() - timedelta(hours=1)
    with self._lock:
        return [event for event in self._recent_changes.values() if event.timestamp >= since]

def add_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
    """Add callback to be called when changes are detected."""
    self._change_callbacks.append(callback)

def remove_change_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
    """Remove change callback."""
    if callback in self._change_callbacks:
        self._change_callbacks.remove(callback)

def _handle_file_event(self, file_path: str, change_type: ChangeType) -> None:
    """Handle a file system event with deadlock prevention."""
    try:
        if self._stop_processing.is_set():
            return
        path = Path(file_path)
        if not self._is_relevant_file(path):
            return
        event = self._create_change_event(path, change_type)
        if not event:
            return
        try:
            with self._lock:
                if not self._stop_processing.is_set():
                    self._event_queue.append(event)
                else:
                    return
        except Exception as lock_error:
            logger.warning(f'Could not acquire lock for file event {file_path}: {lock_error}')
            return
        self._schedule_debounced_processing(str(path))
    except Exception as e:
        logger.error(f'Error handling file event for {file_path}: {e}')

def _is_relevant_file(self, path: Path) -> bool:
    """Check if file is relevant for monitoring."""
    try:
        path = path.resolve()
        if not str(path).startswith(str(self.project_path)):
            return False
        import fnmatch
        filename = path.name
        for pattern in self._excluded_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return False
        for parent in path.parents:
            if parent.name in {'__pycache__', '.git', 'node_modules'}:
                return False
        return True
    except Exception as e:
        logger.error(f'Error checking file relevance for {path}: {e}')
        return False

def _create_change_event(self, path: Path, change_type: ChangeType) -> Optional[FileChangeEvent]:
    """Create a FileChangeEvent from path and change type."""
    try:
        file_size = None
        if change_type != ChangeType.DELETED and path.exists():
            try:
                file_size = path.stat().st_size
            except OSError:
                pass
        affects_sync = self._should_trigger_sync(path)
        analysis = self.content_analyzer.analyze_file_change(path, change_type.value)
        event = FileChangeEvent(file_path=path, change_type=change_type, timestamp=datetime.now(), affects_sync=affects_sync, file_size=file_size, content_hash=analysis.get('content_hash'), previous_content_hash=analysis.get('previous_content_hash'), is_significant_change=analysis.get('is_significant_change', True), media_metadata=analysis.get('media_metadata'), git_info=analysis.get('git_info'), content_type=analysis.get('content_type'))
        return event
    except Exception as e:
        logger.error(f'Error creating change event for {path}: {e}')
        return None

def _should_trigger_sync(self, path: Path) -> bool:
    """Check if file change should trigger sync."""
    import fnmatch
    filename = path.name
    relative_path_obj = safe_relative_to(path, self.project_path)
    if relative_path_obj is None:
        return False
    relative_path = str(relative_path_obj)
    for pattern in self.config.watch_patterns:
        if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(relative_path, pattern):
            return True
    return False

def _cleanup(self) -> None:
    """Clean up resources."""
    self._is_monitoring = False
    self._observer = None
    self._event_handler = None
    self._processing_thread = None
    self._watch_paths.clear()
    self._event_queue.clear()
    self._recent_changes.clear()

def __enter__(self):
    """Context manager entry."""
    self.start_monitoring()
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit."""
    self.stop_monitoring()
