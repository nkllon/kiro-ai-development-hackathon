"""
Message History Services Services

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

class MessageHistoryManager:
    """
    Comprehensive message history and retrieval system.
    
    Provides advanced filtering, search, and status tracking
    capabilities for Beast Mode agent messages.
    """

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

    async def start(self) -> None:
        """Start the message history manager"""
        if self.is_running:
            logger.warning('Message history manager is already running')
            return
        self.is_running = True
        self.auto_save_task = asyncio.create_task(self._auto_save_loop())
        logger.info('Message history manager started')

    async def stop(self) -> None:
        """Stop the message history manager"""
        if not self.is_running:
            return
        self.is_running = False
        if self.auto_save_task and (not self.auto_save_task.done()):
            self.auto_save_task.cancel()
            try:
                await self.auto_save_task
            except asyncio.CancelledError:
                pass
        await self._save_status_data()
        logger.info('Message history manager stopped')

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

    async def _save_status_data(self) -> None:
        """Save message status data to file"""
        if not self.status_dirty:
            return
        try:
            data = {'message_status': self.message_status, 'last_updated': datetime.now().isoformat(), 'stats': self.stats}
            temp_file = self.status_file.with_suffix('.tmp')
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_status_file, temp_file, data)
            await loop.run_in_executor(None, temp_file.replace, self.status_file)
            self.status_dirty = False
            self.stats['last_save_time'] = datetime.now()
            logger.debug('Message status data saved')
        except Exception as e:
            logger.error(f'Error saving status data: {e}')

    def _write_status_file(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Synchronous status file write"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    async def _auto_save_loop(self) -> None:
        """Background loop for auto-saving status data"""
        try:
            while self.is_running:
                await asyncio.sleep(self.auto_save_interval)
                if self.is_running and self.status_dirty:
                    await self._save_status_data()
        except asyncio.CancelledError:
            logger.info('Auto-save loop cancelled')
        except Exception as e:
            logger.error(f'Error in auto-save loop: {e}')

    async def scan_messages(self, filter_criteria: Optional[MessageFilter]=None, force_rescan: bool=False) -> List[MessageEntry]:
        """
        Scan log files and retrieve messages based on filter criteria.
        
        Args:
            filter_criteria: Filter criteria for message selection
            force_rescan: Force rescan even if cached results exist
            
        Returns:
            List of matching message entries
        """
        if filter_criteria is None:
            filter_criteria = MessageFilter()
        try:
            messages = []
            log_files = await self._get_log_files()
            for log_file_info in log_files:
                file_path = Path(log_file_info['path'])
                if not self._file_in_time_range(log_file_info, filter_criteria):
                    continue
                file_messages = await self._scan_log_file(file_path, filter_criteria)
                messages.extend(file_messages)
                if filter_criteria.limit:
                    total_needed = filter_criteria.offset + filter_criteria.limit
                    if len(messages) >= total_needed:
                        break
            messages = self._apply_final_filters(messages, filter_criteria)
            self.stats['messages_scanned'] += len(messages)
            self.stats['last_scan_time'] = datetime.now()
            self.stats['searches_performed'] += 1
            return messages
        except Exception as e:
            logger.error(f'Error scanning messages: {e}')
            return []

    async def _get_log_files(self) -> List[Dict[str, Any]]:
        """Get information about all log files"""
        log_files = []
        try:
            for file_path in self.log_directory.glob('mailbox_*.log'):
                if file_path.is_file():
                    stat = file_path.stat()
                    log_files.append({'path': str(file_path), 'size_bytes': stat.st_size, 'created': datetime.fromtimestamp(stat.st_ctime), 'modified': datetime.fromtimestamp(stat.st_mtime)})
            log_files.sort(key=lambda x: x['created'], reverse=True)
        except Exception as e:
            logger.error(f'Error getting log file information: {e}')
        return log_files

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

    async def _scan_log_file(self, file_path: Path, filter_criteria: MessageFilter) -> List[MessageEntry]:
        """Scan a single log file for matching messages"""
        messages = []
        try:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, self._read_log_file, file_path)
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                try:
                    log_entry = json.loads(line)
                    if not log_entry.get('parsed_message'):
                        continue
                    message_entry = self._create_message_entry(log_entry, str(file_path))
                    if self._message_matches_filter(message_entry, filter_criteria):
                        messages.append(message_entry)
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    logger.debug(f'Error processing log line: {e}')
                    continue
        except Exception as e:
            logger.error(f'Error scanning log file {file_path}: {e}')
        return messages

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

    async def check_mail(self, agent_id: str, since: Optional[datetime]=None, message_types: Optional[List[MessageType]]=None, limit: Optional[int]=None, mark_as_read: bool=True) -> List[MessageEntry]:
        """
        Check mail for a specific agent.
        
        Args:
            agent_id: Agent ID to check mail for
            since: Only return messages after this timestamp
            message_types: Filter by message types
            limit: Maximum number of messages to return
            mark_as_read: Whether to mark retrieved messages as read
            
        Returns:
            List of message entries for the agent
        """
        filter_criteria = MessageFilter(since=since, message_types=message_types, target_agents=[agent_id], status=[MessageStatus.UNREAD] if mark_as_read else None, limit=limit)
        messages = await self.scan_messages(filter_criteria)
        if mark_as_read:
            for message_entry in messages:
                await self.mark_message_read(message_entry.message.id)
        return messages

    async def search_messages(self, search_text: str, agent_id: Optional[str]=None, message_types: Optional[List[MessageType]]=None, since: Optional[datetime]=None, limit: Optional[int]=50) -> List[MessageEntry]:
        """
        Search messages by text content.
        
        Args:
            search_text: Text to search for
            agent_id: Limit search to messages for specific agent
            message_types: Filter by message types
            since: Only search messages after this timestamp
            limit: Maximum number of results
            
        Returns:
            List of matching message entries
        """
        filter_criteria = MessageFilter(search_text=search_text, target_agents=[agent_id] if agent_id else None, message_types=message_types, since=since, limit=limit)
        return await self.scan_messages(filter_criteria)

    async def get_conversation_thread(self, correlation_id: str, limit: Optional[int]=None) -> List[MessageEntry]:
        """
        Get all messages in a conversation thread.
        
        Args:
            correlation_id: Correlation ID of the conversation
            limit: Maximum number of messages to return
            
        Returns:
            List of message entries in the conversation
        """
        filter_criteria = MessageFilter(correlation_ids=[correlation_id], limit=limit)
        messages = await self.scan_messages(filter_criteria)
        messages.sort(key=lambda x: x.log_timestamp)
        return messages

    async def mark_message_read(self, message_id: str) -> None:
        """Mark a message as read"""
        await self._update_message_status(message_id, MessageStatus.READ, read_timestamp=datetime.now())

    async def mark_message_unread(self, message_id: str) -> None:
        """Mark a message as unread"""
        await self._update_message_status(message_id, MessageStatus.UNREAD)

    async def archive_message(self, message_id: str) -> None:
        """Archive a message"""
        await self._update_message_status(message_id, MessageStatus.ARCHIVED)

    async def flag_message(self, message_id: str) -> None:
        """Flag a message for attention"""
        await self._update_message_status(message_id, MessageStatus.FLAGGED)

    async def add_message_tag(self, message_id: str, tag: str) -> None:
        """Add a tag to a message"""
        if message_id not in self.message_status:
            self.message_status[message_id] = {}
        if 'tags' not in self.message_status[message_id]:
            self.message_status[message_id]['tags'] = []
        if tag not in self.message_status[message_id]['tags']:
            self.message_status[message_id]['tags'].append(tag)
            self.status_dirty = True
            self.stats['status_updates'] += 1

    async def remove_message_tag(self, message_id: str, tag: str) -> None:
        """Remove a tag from a message"""
        if message_id in self.message_status:
            tags = self.message_status[message_id].get('tags', [])
            if tag in tags:
                tags.remove(tag)
                self.status_dirty = True
                self.stats['status_updates'] += 1

    async def add_message_note(self, message_id: str, note: str) -> None:
        """Add a note to a message"""
        if message_id not in self.message_status:
            self.message_status[message_id] = {}
        self.message_status[message_id]['notes'] = note
        self.status_dirty = True
        self.stats['status_updates'] += 1

    async def _update_message_status(self, message_id: str, status: MessageStatus, read_timestamp: Optional[datetime]=None) -> None:
        """Update message status"""
        if message_id not in self.message_status:
            self.message_status[message_id] = {}
        self.message_status[message_id]['status'] = status.value
        if read_timestamp:
            self.message_status[message_id]['read_timestamp'] = read_timestamp.isoformat()
        elif status == MessageStatus.UNREAD:
            self.message_status[message_id].pop('read_timestamp', None)
        self.status_dirty = True
        self.stats['status_updates'] += 1

    async def get_message_counts(self, agent_id: Optional[str]=None, since: Optional[datetime]=None) -> Dict[str, int]:
        """
        Get message counts by status.
        
        Args:
            agent_id: Count messages for specific agent
            since: Only count messages after this timestamp
            
        Returns:
            Dictionary with counts by status
        """
        filter_criteria = MessageFilter(target_agents=[agent_id] if agent_id else None, since=since)
        messages = await self.scan_messages(filter_criteria)
        counts = {status.value: 0 for status in MessageStatus}
        for message_entry in messages:
            counts[message_entry.status.value] += 1
        counts['total'] = len(messages)
        return counts

    async def cleanup_old_status(self, days_old: int=30) -> int:
        """
        Clean up status data for old messages.
        
        Args:
            days_old: Remove status for messages older than this many days
            
        Returns:
            Number of status entries removed
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        removed_count = 0
        existing_messages = set()
        filter_criteria = MessageFilter(since=cutoff_date)
        messages = await self.scan_messages(filter_criteria)
        for message_entry in messages:
            existing_messages.add(message_entry.message.id)
        to_remove = []
        for message_id in self.message_status:
            if message_id not in existing_messages:
                to_remove.append(message_id)
        for message_id in to_remove:
            del self.message_status[message_id]
            removed_count += 1
        if removed_count > 0:
            self.status_dirty = True
            logger.info(f'Cleaned up status for {removed_count} old messages')
        return removed_count

    def get_stats(self) -> Dict[str, Any]:
        """Get message history manager statistics"""
        return {**self.stats, 'is_running': self.is_running, 'message_status_count': len(self.message_status), 'cache_size': len(self.message_cache), 'status_dirty': self.status_dirty, 'log_directory': str(self.log_directory)}

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the message history manager"""
        return {'status': 'healthy' if self.is_running else 'stopped', 'is_running': self.is_running, 'log_directory': str(self.log_directory), 'status_file': str(self.status_file), 'stats': self.get_stats()}
