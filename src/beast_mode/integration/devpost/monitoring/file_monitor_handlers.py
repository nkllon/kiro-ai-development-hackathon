"""
File Monitor Handlers

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

class DevpostFileEventHandler(FileSystemEventHandler):
    """Custom file system event handler for Devpost integration."""

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
