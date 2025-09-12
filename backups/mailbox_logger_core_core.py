"""
Mailbox Logger Core Core

This module was extracted from mailbox_logger_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import logging
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError
from .models import BeastModeMessage, MessageType

class MailboxLogger:
    """
    Persistent mailbox logger that runs continuously in background.
    
    Captures all messages from the Beast Mode network and logs them
    with full content preservation for later retrieval.
    """

    def __init__(self, redis_url: str='redis://localhost:6379', log_directory: str='beast_mode_mailbox', channel: str='beast_mode_network', max_log_size_mb: int=100, max_log_files: int=10, rotation_check_interval: int=300):
        self.redis_url = redis_url
        self.log_directory = Path(log_directory)
        self.channel = channel
        self.max_log_size_bytes = max_log_size_mb * 1024 * 1024
        self.max_log_files = max_log_files
        self.rotation_check_interval = rotation_check_interval
        self.client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.is_running = False
        self.is_connected = False
        self.logger_task: Optional[asyncio.Task] = None
        self.rotation_task: Optional[asyncio.Task] = None
        self.current_log_file: Optional[Path] = None
        self.current_log_handle = None
        self.stats = {'messages_logged': 0, 'parsing_errors': 0, 'connection_errors': 0, 'log_rotations': 0, 'start_time': None, 'last_message_time': None, 'current_log_size': 0}
        self.log_directory.mkdir(parents=True, exist_ok=True)
        self._initialize_log_file()

    def _initialize_log_file(self) -> None:
        """Initialize the current log file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_log_file = self.log_directory / f'mailbox_{timestamp}.log'
        try:
            self.current_log_handle = open(self.current_log_file, 'a', encoding='utf-8')
            logger.info(f'Initialized log file: {self.current_log_file}')
        except Exception as e:
            logger.error(f'Failed to initialize log file: {e}')
            raise

    async def start_logging(self) -> None:
        """Start the continuous background logging process"""
        if self.is_running:
            logger.warning('Mailbox logger is already running')
            return
        try:
            await self._connect_redis()
            self.is_running = True
            self.stats['start_time'] = datetime.now()
            self.logger_task = asyncio.create_task(self._message_logger_loop())
            self.rotation_task = asyncio.create_task(self._rotation_manager_loop())
            logger.info('Mailbox logger started successfully')
        except Exception as e:
            logger.error(f'Failed to start mailbox logger: {e}')
            await self.stop_logging()
            raise

    async def stop_logging(self) -> None:
        """Stop the background logging process"""
        logger.info('Stopping mailbox logger...')
        self.is_running = False
        if self.logger_task and (not self.logger_task.done()):
            self.logger_task.cancel()
            try:
                await self.logger_task
            except asyncio.CancelledError:
                pass
        if self.rotation_task and (not self.rotation_task.done()):
            self.rotation_task.cancel()
            try:
                await self.rotation_task
            except asyncio.CancelledError:
                pass
        await self._disconnect_redis()
        if self.current_log_handle:
            try:
                self.current_log_handle.close()
                self.current_log_handle = None
            except Exception as e:
                logger.error(f'Error closing log file: {e}')
        logger.info('Mailbox logger stopped')

    async def _connect_redis(self) -> None:
        """Connect to Redis with retry logic"""
        max_retries = 5
        retry_delay = 1.0
        for attempt in range(max_retries):
            try:
                logger.info(f'Connecting to Redis (attempt {attempt + 1}/{max_retries})')
                self.client = redis.from_url(self.redis_url, socket_connect_timeout=10.0, socket_timeout=10.0, retry_on_timeout=True, decode_responses=True)
                await self.client.ping()
                self.is_connected = True
                logger.info(f'Connected to Redis at {self.redis_url}')
                return
            except (ConnectionError, TimeoutError) as e:
                self.stats['connection_errors'] += 1
                logger.warning(f'Connection attempt {attempt + 1} failed: {e}')
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * 2 ** attempt)
                else:
                    raise ConnectionError(f'Failed to connect to Redis after {max_retries} attempts')
            except Exception as e:
                logger.error(f'Unexpected error connecting to Redis: {e}')
                raise

    async def _disconnect_redis(self) -> None:
        """Disconnect from Redis"""
        try:
            if self.pubsub:
                await self.pubsub.unsubscribe(self.channel)
                await self.pubsub.aclose()
                self.pubsub = None
            if self.client:
                await self.client.aclose()
                self.client = None
            self.is_connected = False
            logger.info('Disconnected from Redis')
        except Exception as e:
            logger.error(f'Error during Redis disconnect: {e}')

    async def _message_logger_loop(self) -> None:
        """Main message logging loop"""
        try:
            self.pubsub = self.client.pubsub()
            await self.pubsub.subscribe(self.channel)
            logger.info(f'Started logging messages from channel: {self.channel}')
            async for raw_message in self.pubsub.listen():
                if not self.is_running:
                    break
                if raw_message['type'] == 'message':
                    await self._log_message(raw_message)
        except asyncio.CancelledError:
            logger.info('Message logger loop cancelled')
        except Exception as e:
            logger.error(f'Error in message logger loop: {e}')
            if self.is_running:
                await self._handle_connection_error()

    async def _log_message(self, raw_message: Dict[str, Any]) -> None:
        """Log a single message with full content preservation"""
        timestamp = datetime.now()
        try:
            log_entry = {'timestamp': timestamp.isoformat(), 'channel': raw_message.get('channel', self.channel), 'raw_data': raw_message['data'], 'parsed_message': None, 'parsing_error': None}
            try:
                message_data = json.loads(raw_message['data'])
                message = BeastModeMessage(**message_data)
                log_entry['parsed_message'] = message.model_dump()
            except json.JSONDecodeError as e:
                log_entry['parsing_error'] = f'JSON decode error: {str(e)}'
                self.stats['parsing_errors'] += 1
            except Exception as e:
                log_entry['parsing_error'] = f'Message validation error: {str(e)}'
                self.stats['parsing_errors'] += 1
            await self._write_log_entry(log_entry)
            self.stats['messages_logged'] += 1
            self.stats['last_message_time'] = timestamp
        except Exception as e:
            logger.error(f'Error logging message: {e}')

    async def _write_log_entry(self, log_entry: Dict[str, Any]) -> None:
        """Write a log entry to the current log file"""
        try:
            log_line = json.dumps(log_entry, default=str) + '\n'
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_to_file, log_line)
            self.stats['current_log_size'] += len(log_line.encode('utf-8'))
        except Exception as e:
            logger.error(f'Error writing log entry: {e}')
            raise

    def _write_to_file(self, log_line: str) -> None:
        """Synchronous file write operation"""
        if self.current_log_handle:
            self.current_log_handle.write(log_line)
            self.current_log_handle.flush()

    async def _rotation_manager_loop(self) -> None:
        """Background loop for log rotation management"""
        try:
            while self.is_running:
                await asyncio.sleep(self.rotation_check_interval)
                if self.is_running:
                    await self._check_log_rotation()
        except asyncio.CancelledError:
            logger.info('Rotation manager loop cancelled')
        except Exception as e:
            logger.error(f'Error in rotation manager loop: {e}')

    async def _check_log_rotation(self) -> None:
        """Check if log rotation is needed and perform it"""
        try:
            if self.stats['current_log_size'] >= self.max_log_size_bytes:
                await self._rotate_log_file()
            await self._cleanup_old_logs()
        except Exception as e:
            logger.error(f'Error during log rotation check: {e}')

    async def _rotate_log_file(self) -> None:
        """Rotate the current log file"""
        try:
            logger.info('Rotating log file...')
            if self.current_log_handle:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.current_log_handle.close)
                self.current_log_handle = None
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._initialize_log_file)
            self.stats['current_log_size'] = 0
            self.stats['log_rotations'] += 1
            logger.info(f'Log rotated to: {self.current_log_file}')
        except Exception as e:
            logger.error(f'Error rotating log file: {e}')
            raise

    async def _cleanup_old_logs(self) -> None:
        """Clean up old log files beyond the retention limit"""
        try:
            log_files = []
            for file_path in self.log_directory.glob('mailbox_*.log'):
                if file_path.is_file():
                    stat = file_path.stat()
                    log_files.append((file_path, stat.st_mtime))
            log_files.sort(key=lambda x: x[1], reverse=True)
            if len(log_files) > self.max_log_files:
                files_to_remove = log_files[self.max_log_files:]
                for file_path, _ in files_to_remove:
                    try:
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, file_path.unlink)
                        logger.info(f'Removed old log file: {file_path}')
                    except Exception as e:
                        logger.error(f'Error removing old log file {file_path}: {e}')
        except Exception as e:
            logger.error(f'Error during log cleanup: {e}')

    async def _handle_connection_error(self) -> None:
        """Handle Redis connection errors with reconnection logic"""
        logger.warning('Handling connection error, attempting to reconnect...')
        try:
            await self._disconnect_redis()
            await asyncio.sleep(5.0)
            if self.is_running:
                await self._connect_redis()
                logger.info('Reconnected to Redis successfully')
        except Exception as e:
            logger.error(f'Failed to reconnect to Redis: {e}')

    def save_full_content(self, message: BeastModeMessage) -> str:
        """
        Save full message content to a separate detailed log.
        
        Args:
            message: The message to save
            
        Returns:
            str: Path to the saved content file
        """
        try:
            content_dir = self.log_directory / 'detailed_content'
            content_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'message_{timestamp}_{message.id[:8]}.json'
            content_file = content_dir / filename
            detailed_content = {'message': message.model_dump(), 'saved_at': datetime.now().isoformat(), 'logger_stats': self.get_logger_stats()}
            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_content, f, indent=2, default=str)
            logger.debug(f'Saved detailed content to: {content_file}')
            return str(content_file)
        except Exception as e:
            logger.error(f'Error saving detailed content: {e}')
            raise

    def get_logger_stats(self) -> Dict[str, Any]:
        """Get current logger statistics"""
        stats = self.stats.copy()
        if stats['start_time']:
            runtime = datetime.now() - stats['start_time']
            stats['runtime_seconds'] = runtime.total_seconds()
        stats.update({'is_running': self.is_running, 'is_connected': self.is_connected, 'current_log_file': str(self.current_log_file) if self.current_log_file else None, 'log_directory': str(self.log_directory), 'channel': self.channel})
        return stats

    def get_log_files(self) -> List[Dict[str, Any]]:
        """Get information about all log files"""
        log_files = []
        try:
            for file_path in self.log_directory.glob('mailbox_*.log'):
                if file_path.is_file():
                    stat = file_path.stat()
                    log_files.append({'path': str(file_path), 'size_bytes': stat.st_size, 'size_mb': round(stat.st_size / (1024 * 1024), 2), 'created': datetime.fromtimestamp(stat.st_ctime).isoformat(), 'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(), 'is_current': file_path == self.current_log_file})
            log_files.sort(key=lambda x: x['created'], reverse=True)
        except Exception as e:
            logger.error(f'Error getting log file information: {e}')
        return log_files

    async def check_mail(self, since: Optional[datetime]=None, message_types: Optional[List[MessageType]]=None, source_agents: Optional[List[str]]=None, limit: Optional[int]=None) -> List[Dict[str, Any]]:
        """
        Check mail by scanning log files for messages.
        
        Args:
            since: Only return messages after this timestamp
            message_types: Filter by message types
            source_agents: Filter by source agent IDs
            limit: Maximum number of messages to return
            
        Returns:
            List of matching messages
        """
        messages = []
        try:
            log_files = self.get_log_files()
            for log_file_info in log_files:
                file_path = Path(log_file_info['path'])
                if since:
                    file_modified = datetime.fromisoformat(log_file_info['modified'])
                    if file_modified < since:
                        continue
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                log_entry = json.loads(line)
                                if since:
                                    entry_time = datetime.fromisoformat(log_entry['timestamp'])
                                    if entry_time < since:
                                        continue
                                if log_entry.get('parsed_message'):
                                    message_data = log_entry['parsed_message']
                                    if message_types and message_data.get('type') not in message_types:
                                        continue
                                    if source_agents and message_data.get('source') not in source_agents:
                                        continue
                                    messages.append({'log_timestamp': log_entry['timestamp'], 'message': message_data, 'log_file': str(file_path)})
                                if limit and len(messages) >= limit:
                                    break
                            except json.JSONDecodeError:
                                continue
                except Exception as e:
                    logger.error(f'Error reading log file {file_path}: {e}')
                    continue
                if limit and len(messages) >= limit:
                    break
            messages.sort(key=lambda x: x['log_timestamp'], reverse=True)
            if limit:
                messages = messages[:limit]
        except Exception as e:
            logger.error(f'Error checking mail: {e}')
        return messages

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the mailbox logger"""
        return {'status': 'healthy' if self.is_running and self.is_connected else 'unhealthy', 'is_running': self.is_running, 'is_connected': self.is_connected, 'redis_url': self.redis_url, 'channel': self.channel, 'log_directory': str(self.log_directory), 'current_log_file': str(self.current_log_file) if self.current_log_file else None, 'stats': self.get_logger_stats(), 'log_files': len(self.get_log_files())}

def __init__(self, redis_url: str='redis://localhost:6379', log_directory: str='beast_mode_mailbox', channel: str='beast_mode_network', max_log_size_mb: int=100, max_log_files: int=10, rotation_check_interval: int=300):
    self.redis_url = redis_url
    self.log_directory = Path(log_directory)
    self.channel = channel
    self.max_log_size_bytes = max_log_size_mb * 1024 * 1024
    self.max_log_files = max_log_files
    self.rotation_check_interval = rotation_check_interval
    self.client: Optional[redis.Redis] = None
    self.pubsub: Optional[redis.client.PubSub] = None
    self.is_running = False
    self.is_connected = False
    self.logger_task: Optional[asyncio.Task] = None
    self.rotation_task: Optional[asyncio.Task] = None
    self.current_log_file: Optional[Path] = None
    self.current_log_handle = None
    self.stats = {'messages_logged': 0, 'parsing_errors': 0, 'connection_errors': 0, 'log_rotations': 0, 'start_time': None, 'last_message_time': None, 'current_log_size': 0}
    self.log_directory.mkdir(parents=True, exist_ok=True)
    self._initialize_log_file()

def _initialize_log_file(self) -> None:
    """Initialize the current log file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    self.current_log_file = self.log_directory / f'mailbox_{timestamp}.log'
    try:
        self.current_log_handle = open(self.current_log_file, 'a', encoding='utf-8')
        logger.info(f'Initialized log file: {self.current_log_file}')
    except Exception as e:
        logger.error(f'Failed to initialize log file: {e}')
        raise

def _write_to_file(self, log_line: str) -> None:
    """Synchronous file write operation"""
    if self.current_log_handle:
        self.current_log_handle.write(log_line)
        self.current_log_handle.flush()

def save_full_content(self, message: BeastModeMessage) -> str:
    """
        Save full message content to a separate detailed log.
        
        Args:
            message: The message to save
            
        Returns:
            str: Path to the saved content file
        """
    try:
        content_dir = self.log_directory / 'detailed_content'
        content_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'message_{timestamp}_{message.id[:8]}.json'
        content_file = content_dir / filename
        detailed_content = {'message': message.model_dump(), 'saved_at': datetime.now().isoformat(), 'logger_stats': self.get_logger_stats()}
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_content, f, indent=2, default=str)
        logger.debug(f'Saved detailed content to: {content_file}')
        return str(content_file)
    except Exception as e:
        logger.error(f'Error saving detailed content: {e}')
        raise

def get_logger_stats(self) -> Dict[str, Any]:
    """Get current logger statistics"""
    stats = self.stats.copy()
    if stats['start_time']:
        runtime = datetime.now() - stats['start_time']
        stats['runtime_seconds'] = runtime.total_seconds()
    stats.update({'is_running': self.is_running, 'is_connected': self.is_connected, 'current_log_file': str(self.current_log_file) if self.current_log_file else None, 'log_directory': str(self.log_directory), 'channel': self.channel})
    return stats

def get_log_files(self) -> List[Dict[str, Any]]:
    """Get information about all log files"""
    log_files = []
    try:
        for file_path in self.log_directory.glob('mailbox_*.log'):
            if file_path.is_file():
                stat = file_path.stat()
                log_files.append({'path': str(file_path), 'size_bytes': stat.st_size, 'size_mb': round(stat.st_size / (1024 * 1024), 2), 'created': datetime.fromtimestamp(stat.st_ctime).isoformat(), 'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(), 'is_current': file_path == self.current_log_file})
        log_files.sort(key=lambda x: x['created'], reverse=True)
    except Exception as e:
        logger.error(f'Error getting log file information: {e}')
    return log_files

def get_health_status(self) -> Dict[str, Any]:
    """Get health status of the mailbox logger"""
    return {'status': 'healthy' if self.is_running and self.is_connected else 'unhealthy', 'is_running': self.is_running, 'is_connected': self.is_connected, 'redis_url': self.redis_url, 'channel': self.channel, 'log_directory': str(self.log_directory), 'current_log_file': str(self.current_log_file) if self.current_log_file else None, 'stats': self.get_logger_stats(), 'log_files': len(self.get_log_files())}

def __init__(self, **logger_kwargs):
    self.logger = MailboxLogger(**logger_kwargs)
    self.background_thread: Optional[threading.Thread] = None
    self.event_loop: Optional[asyncio.AbstractEventLoop] = None
    self.is_running = False

def start(self) -> None:
    """Start the mailbox logger in a background thread"""
    if self.is_running:
        logger.warning('MailboxLogger is already running')
        return

    def run_logger():
        """Run the logger in its own event loop"""
        try:
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            self.event_loop.run_until_complete(self.logger.start_logging())
            self.event_loop.run_forever()
        except Exception as e:
            logger.error(f'Error in background logger thread: {e}')
        finally:
            if self.event_loop:
                self.event_loop.close()
    self.background_thread = threading.Thread(target=run_logger, daemon=True)
    self.background_thread.start()
    self.is_running = True
    logger.info('MailboxLogger started in background thread')

def stop(self) -> None:
    """Stop the mailbox logger"""
    if not self.is_running:
        return
    try:
        if self.event_loop and (not self.event_loop.is_closed()):
            future = asyncio.run_coroutine_threadsafe(self.logger.stop_logging(), self.event_loop)
            future.result(timeout=10.0)
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)
        if self.background_thread and self.background_thread.is_alive():
            self.background_thread.join(timeout=5.0)
        self.is_running = False
        logger.info('MailboxLogger stopped')
    except Exception as e:
        logger.error(f'Error stopping MailboxLogger: {e}')

def get_status(self) -> Dict[str, Any]:
    """Get status of the logger manager"""
    return {'manager_running': self.is_running, 'thread_alive': self.background_thread.is_alive() if self.background_thread else False, 'logger_status': self.logger.get_health_status()}

def __enter__(self):
    """Context manager entry"""
    self.start()
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit"""
    self.stop()

def run_logger():
    """Run the logger in its own event loop"""
    try:
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_until_complete(self.logger.start_logging())
        self.event_loop.run_forever()
    except Exception as e:
        logger.error(f'Error in background logger thread: {e}')
    finally:
        if self.event_loop:
            self.event_loop.close()

def __init__(self, redis_url: str='redis://localhost:6379', log_directory: str='beast_mode_mailbox', channel: str='beast_mode_network', max_log_size_mb: int=100, max_log_files: int=10, rotation_check_interval: int=300):
    self.redis_url = redis_url
    self.log_directory = Path(log_directory)
    self.channel = channel
    self.max_log_size_bytes = max_log_size_mb * 1024 * 1024
    self.max_log_files = max_log_files
    self.rotation_check_interval = rotation_check_interval
    self.client: Optional[redis.Redis] = None
    self.pubsub: Optional[redis.client.PubSub] = None
    self.is_running = False
    self.is_connected = False
    self.logger_task: Optional[asyncio.Task] = None
    self.rotation_task: Optional[asyncio.Task] = None
    self.current_log_file: Optional[Path] = None
    self.current_log_handle = None
    self.stats = {'messages_logged': 0, 'parsing_errors': 0, 'connection_errors': 0, 'log_rotations': 0, 'start_time': None, 'last_message_time': None, 'current_log_size': 0}
    self.log_directory.mkdir(parents=True, exist_ok=True)
    self._initialize_log_file()

def _initialize_log_file(self) -> None:
    """Initialize the current log file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    self.current_log_file = self.log_directory / f'mailbox_{timestamp}.log'
    try:
        self.current_log_handle = open(self.current_log_file, 'a', encoding='utf-8')
        logger.info(f'Initialized log file: {self.current_log_file}')
    except Exception as e:
        logger.error(f'Failed to initialize log file: {e}')
        raise

def _write_to_file(self, log_line: str) -> None:
    """Synchronous file write operation"""
    if self.current_log_handle:
        self.current_log_handle.write(log_line)
        self.current_log_handle.flush()

def save_full_content(self, message: BeastModeMessage) -> str:
    """
        Save full message content to a separate detailed log.
        
        Args:
            message: The message to save
            
        Returns:
            str: Path to the saved content file
        """
    try:
        content_dir = self.log_directory / 'detailed_content'
        content_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'message_{timestamp}_{message.id[:8]}.json'
        content_file = content_dir / filename
        detailed_content = {'message': message.model_dump(), 'saved_at': datetime.now().isoformat(), 'logger_stats': self.get_logger_stats()}
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_content, f, indent=2, default=str)
        logger.debug(f'Saved detailed content to: {content_file}')
        return str(content_file)
    except Exception as e:
        logger.error(f'Error saving detailed content: {e}')
        raise

def get_logger_stats(self) -> Dict[str, Any]:
    """Get current logger statistics"""
    stats = self.stats.copy()
    if stats['start_time']:
        runtime = datetime.now() - stats['start_time']
        stats['runtime_seconds'] = runtime.total_seconds()
    stats.update({'is_running': self.is_running, 'is_connected': self.is_connected, 'current_log_file': str(self.current_log_file) if self.current_log_file else None, 'log_directory': str(self.log_directory), 'channel': self.channel})
    return stats

def get_log_files(self) -> List[Dict[str, Any]]:
    """Get information about all log files"""
    log_files = []
    try:
        for file_path in self.log_directory.glob('mailbox_*.log'):
            if file_path.is_file():
                stat = file_path.stat()
                log_files.append({'path': str(file_path), 'size_bytes': stat.st_size, 'size_mb': round(stat.st_size / (1024 * 1024), 2), 'created': datetime.fromtimestamp(stat.st_ctime).isoformat(), 'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(), 'is_current': file_path == self.current_log_file})
        log_files.sort(key=lambda x: x['created'], reverse=True)
    except Exception as e:
        logger.error(f'Error getting log file information: {e}')
    return log_files

def get_health_status(self) -> Dict[str, Any]:
    """Get health status of the mailbox logger"""
    return {'status': 'healthy' if self.is_running and self.is_connected else 'unhealthy', 'is_running': self.is_running, 'is_connected': self.is_connected, 'redis_url': self.redis_url, 'channel': self.channel, 'log_directory': str(self.log_directory), 'current_log_file': str(self.current_log_file) if self.current_log_file else None, 'stats': self.get_logger_stats(), 'log_files': len(self.get_log_files())}

def run_logger():
    """Run the logger in its own event loop"""
    try:
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_until_complete(self.logger.start_logging())
        self.event_loop.run_forever()
    except Exception as e:
        logger.error(f'Error in background logger thread: {e}')
    finally:
        if self.event_loop:
            self.event_loop.close()
