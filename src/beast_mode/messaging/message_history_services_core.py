"""
Message History Services Core

This module was extracted from message_history_services.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from .models import BeastModeMessage, MessageType, AgentCapabilities
from src.rm_ddd.core.health import ModuleHealth


def __init__(self, log_directory: str='beast_mode_mailbox', status_file: str='message_status.json', cache_size: int=1000, auto_save_interval: int=300):
    self.log_directory = Path(log_directory)
    self.status_file = self.log_directory / status_file
    self.cache_size = cache_size
    self.auto_save_interval = auto_save_interval
    self.message_status: Dict[str, Dict[str, Any]] = {}
    self.status_dirty = False
    self.message_cache: Dict[str, MessageEntry] = {}
    self.cache_timestamps: Dict[str, datetime] = {}
    self.auto_save_task: Optional[asyncio.Task] = None
    self.is_running = False
    self.stats = {'messages_scanned': 0, 'cache_hits': 0, 'cache_misses': 0, 'status_updates': 0, 'searches_performed': 0, 'last_scan_time': None, 'last_save_time': None}
    self.log_directory.mkdir(parents=True, exist_ok=True)
    self._load_status_data()

def _load_status_data(self) -> None:
    """Load message status data from file"""
    try:
        if self.status_file.exists():
            with open(self.status_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.message_status = data.get('message_status', {})
            logger.info(f'Loaded status for {len(self.message_status)} messages')
        else:
            logger.info('No existing status file found, starting fresh')
    except Exception as e:
        logger.error(f'Error loading status data: {e}')
        self.message_status = {}

def _write_status_file(self, file_path: Path, data: Dict[str, Any]) -> None:
    """Synchronous status file write"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)

def _file_in_time_range(self, log_file_info: Dict[str, Any], filter_criteria: MessageFilter) -> bool:
    """Check if log file is within the time range filter"""
    if not filter_criteria.since and (not filter_criteria.until):
        return True
    file_modified = log_file_info['modified']
    if filter_criteria.since and file_modified < filter_criteria.since:
        return False
    if filter_criteria.until and file_modified > filter_criteria.until:
        return False
    return True

def _read_log_file(self, file_path: Path) -> str:
    """Synchronous log file read"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def _create_message_entry(self, log_entry: Dict[str, Any], log_file: str) -> MessageEntry:
    """Create a MessageEntry from a log entry"""
    message_data = log_entry['parsed_message']
    message = BeastModeMessage(**message_data)
    log_timestamp = datetime.fromisoformat(log_entry['timestamp'])
    message_id = message.id
    status_data = self.message_status.get(message_id, {})
    status = MessageStatus(status_data.get('status', MessageStatus.UNREAD))
    read_timestamp = None
    if status_data.get('read_timestamp'):
        read_timestamp = datetime.fromisoformat(status_data['read_timestamp'])
    tags = set(status_data.get('tags', []))
    notes = status_data.get('notes')
    return MessageEntry(log_timestamp=log_timestamp, message=message, log_file=log_file, status=status, read_timestamp=read_timestamp, tags=tags, notes=notes)

def _message_matches_filter(self, message_entry: MessageEntry, filter_criteria: MessageFilter) -> bool:
    """Check if a message entry matches the filter criteria"""
    message = message_entry.message
    if filter_criteria.since and message_entry.log_timestamp < filter_criteria.since:
        return False
    if filter_criteria.until and message_entry.log_timestamp > filter_criteria.until:
        return False
    if filter_criteria.message_types and message.type not in filter_criteria.message_types:
        return False
    if filter_criteria.source_agents and message.source not in filter_criteria.source_agents:
        return False
    if filter_criteria.target_agents:
        if not message.target or message.target not in filter_criteria.target_agents:
            return False
    if filter_criteria.status and message_entry.status not in filter_criteria.status:
        return False
    if filter_criteria.priority_min and message.priority < filter_criteria.priority_min:
        return False
    if filter_criteria.priority_max and message.priority > filter_criteria.priority_max:
        return False
    if filter_criteria.correlation_ids:
        if not message.correlation_id or message.correlation_id not in filter_criteria.correlation_ids:
            return False
    if filter_criteria.search_text:
        if not self._message_contains_text(message, filter_criteria.search_text):
            return False
    return True

def _message_contains_text(self, message: BeastModeMessage, search_text: str) -> bool:
    """Check if message contains the search text"""
    search_text = search_text.lower()
    searchable_fields = [message.source, message.target or '', str(message.payload), message.type.value]
    for field in searchable_fields:
        if search_text in field.lower():
            return True
    return False

def _apply_final_filters(self, messages: List[MessageEntry], filter_criteria: MessageFilter) -> List[MessageEntry]:
    """Apply final filtering, sorting, and pagination"""
    sort_order = getattr(filter_criteria, 'sort_order', SortOrder.NEWEST_FIRST)
    if sort_order == SortOrder.NEWEST_FIRST:
        messages.sort(key=lambda x: x.log_timestamp, reverse=True)
    elif sort_order == SortOrder.OLDEST_FIRST:
        messages.sort(key=lambda x: x.log_timestamp)
    elif sort_order == SortOrder.PRIORITY_HIGH_FIRST:
        messages.sort(key=lambda x: x.message.priority)
    elif sort_order == SortOrder.PRIORITY_LOW_FIRST:
        messages.sort(key=lambda x: x.message.priority, reverse=True)
    start_idx = filter_criteria.offset
    end_idx = None
    if filter_criteria.limit:
        end_idx = start_idx + filter_criteria.limit
    return messages[start_idx:end_idx]

def get_stats(self) -> Dict[str, Any]:
    """Get message history manager statistics"""
    return {**self.stats, 'is_running': self.is_running, 'message_status_count': len(self.message_status), 'cache_size': len(self.message_cache), 'status_dirty': self.status_dirty, 'log_directory': str(self.log_directory)}

def get_health_status(self) -> Dict[str, Any]:
    """Get health status of the message history manager"""
    return {'status': 'healthy' if self.is_running else 'stopped', 'is_running': self.is_running, 'log_directory': str(self.log_directory), 'status_file': str(self.status_file), 'stats': self.get_stats()}

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

