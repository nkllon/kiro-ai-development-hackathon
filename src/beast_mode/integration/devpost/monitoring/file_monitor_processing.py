"""
File Monitor Processing

This module was extracted from file_monitor.py
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

class ScheduledebouncedprocessingClass:
    """Auto-generated class for functions."""

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
    from src.rm_ddd.core.health import ModuleHealth

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

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

