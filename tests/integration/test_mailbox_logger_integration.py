"""
Integration tests for Beast Mode Mailbox Logger
"""

import asyncio
import json
import pytest
import tempfile
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import redis.asyncio as redis

from src.beast_mode.messaging.mailbox_logger import MailboxLogger, MailboxLoggerManager
from src.beast_mode.messaging.bus_client import BeastModeBusClient
from src.beast_mode.messaging.models import BeastModeMessage, MessageType


class TestMailboxLoggerIntegration:
    """Integration tests for MailboxLogger with real Redis simulation"""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary directory for log files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_redis_client(self):
        """Create a mock Redis client that simulates pub/sub behavior"""
        client = AsyncMock()
        pubsub = AsyncMock()
        
        # Mock successful connection
        client.ping = AsyncMock(return_value=True)
        client.pubsub = MagicMock(return_value=pubsub)
        client.publish = AsyncMock(return_value=1)
        client.aclose = AsyncMock(return_value=None)
        
        # Mock pubsub operations
        pubsub.subscribe = AsyncMock(return_value=None)
        pubsub.unsubscribe = AsyncMock(return_value=None)
        pubsub.aclose = AsyncMock(return_value=None)
        
        return client, pubsub
    
    @pytest.mark.asyncio
    async def test_end_to_end_message_logging(self, temp_log_dir, mock_redis_client):
        """Test complete message logging flow from Redis to log files"""
        client, pubsub = mock_redis_client
        
        # Create test messages
        test_messages = [
            BeastModeMessage(
                type=MessageType.SIMPLE_MESSAGE,
                source="agent_1",
                payload={"content": "Hello from agent 1"}
            ),
            BeastModeMessage(
                type=MessageType.HELP_WANTED,
                source="agent_2",
                payload={"required_capabilities": ["python"], "description": "Need help"}
            ),
            BeastModeMessage(
                type=MessageType.AGENT_DISCOVERY,
                source="agent_3",
                payload={"capabilities": ["gcp", "terraform"]}
            )
        ]
        
        # Convert messages to Redis format
        redis_messages = []
        for msg in test_messages:
            redis_messages.append({
                'type': 'message',
                'channel': 'test_channel',
                'data': json.dumps(msg.model_dump(), default=str)
            })
        
        # Mock the pubsub listen method to return our test messages
        async def mock_listen():
            for msg in redis_messages:
                yield msg
        
        pubsub.listen = mock_listen
        
        # Create logger
        logger = MailboxLogger(
            redis_url="redis://localhost:6379",
            log_directory=temp_log_dir,
            channel="test_channel"
        )
        
        with patch('redis.asyncio.from_url', return_value=client):
            # Start logging
            await logger.start_logging()
            
            # Wait a bit for messages to be processed
            await asyncio.sleep(0.1)
            
            # Stop logging
            await logger.stop_logging()
        
        # Verify messages were logged
        assert logger.stats['messages_logged'] == 3
        assert logger.stats['parsing_errors'] == 0
        
        # Check log file contents
        log_files = logger.get_log_files()
        assert len(log_files) >= 1
        
        # Read and verify log entries
        log_file_path = Path(log_files[0]['path'])
        with open(log_file_path, 'r') as f:
            log_lines = f.readlines()
        
        assert len(log_lines) == 3
        
        for i, line in enumerate(log_lines):
            log_entry = json.loads(line.strip())
            
            assert 'timestamp' in log_entry
            assert log_entry['channel'] == 'test_channel'
            assert log_entry['parsed_message'] is not None
            assert log_entry['parsing_error'] is None
            
            # Verify message content
            parsed_msg = log_entry['parsed_message']
            assert parsed_msg['source'] == test_messages[i].source
            assert parsed_msg['type'] == test_messages[i].type
    
    @pytest.mark.asyncio
    async def test_logger_with_bus_client_simulation(self, temp_log_dir, mock_redis_client):
        """Test logger working alongside a bus client"""
        client, pubsub = mock_redis_client
        
        # Create logger
        logger = MailboxLogger(
            redis_url="redis://localhost:6379",
            log_directory=temp_log_dir,
            channel="beast_mode_network"
        )
        
        # Simulate messages being sent through bus client
        sent_messages = []
        
        async def mock_publish(channel, message_json):
            """Mock Redis publish that feeds messages to logger"""
            message_data = json.loads(message_json)
            redis_message = {
                'type': 'message',
                'channel': channel,
                'data': message_json
            }
            sent_messages.append(redis_message)
        
        client.publish = mock_publish
        
        # Mock pubsub to return sent messages
        async def mock_listen():
            while logger.is_running:
                if sent_messages:
                    yield sent_messages.pop(0)
                else:
                    await asyncio.sleep(0.01)
        
        pubsub.listen = mock_listen
        
        with patch('redis.asyncio.from_url', return_value=client):
            # Start logger
            await logger.start_logging()
            
            # Simulate bus client sending messages
            bus_client = BeastModeBusClient(
                redis_url="redis://localhost:6379",
                agent_id="test_agent",
                capabilities=["testing"]
            )
            
            # Mock bus client connection
            bus_client.client = client
            bus_client.is_connected = True
            
            # Send some messages
            await bus_client.send_simple_message("Hello world!")
            await bus_client.announce_presence()
            
            # Wait for processing
            await asyncio.sleep(0.1)
            
            # Stop logger
            await logger.stop_logging()
        
        # Verify messages were logged
        assert logger.stats['messages_logged'] >= 2
        
        # Check that messages are in log files
        messages = await logger.check_mail()
        assert len(messages) >= 2
        
        # Verify message types
        message_types = [msg['message']['type'] for msg in messages]
        assert MessageType.SIMPLE_MESSAGE in message_types
        assert MessageType.AGENT_DISCOVERY in message_types
    
    @pytest.mark.asyncio
    async def test_log_rotation_during_operation(self, temp_log_dir, mock_redis_client):
        """Test log rotation while logger is actively receiving messages"""
        client, pubsub = mock_redis_client
        
        # Create logger with very small log size for testing rotation
        logger = MailboxLogger(
            redis_url="redis://localhost:6379",
            log_directory=temp_log_dir,
            channel="test_channel",
            max_log_size_mb=0.001,  # 1KB for quick rotation
            rotation_check_interval=1  # Check every second
        )
        
        # Create a stream of messages
        message_count = 0
        
        async def mock_listen():
            nonlocal message_count
            while logger.is_running and message_count < 50:
                message = BeastModeMessage(
                    type=MessageType.SIMPLE_MESSAGE,
                    source=f"agent_{message_count}",
                    payload={"content": f"Message {message_count} with some content to make it larger"}
                )
                
                redis_message = {
                    'type': 'message',
                    'channel': 'test_channel',
                    'data': json.dumps(message.model_dump(), default=str)
                }
                
                message_count += 1
                yield redis_message
                await asyncio.sleep(0.01)  # Small delay between messages
        
        pubsub.listen = mock_listen
        
        with patch('redis.asyncio.from_url', return_value=client):
            # Start logger
            await logger.start_logging()
            
            # Wait for messages and potential rotation
            await asyncio.sleep(2.0)
            
            # Stop logger
            await logger.stop_logging()
        
        # Check that rotation occurred
        log_files = logger.get_log_files()
        
        # Should have multiple log files due to rotation
        assert len(log_files) > 1 or logger.stats['log_rotations'] > 0
        
        # Verify all messages were logged across files
        total_messages = 0
        for log_file_info in log_files:
            with open(log_file_info['path'], 'r') as f:
                lines = f.readlines()
                total_messages += len(lines)
        
        assert total_messages == logger.stats['messages_logged']
        assert logger.stats['messages_logged'] > 0
    
    @pytest.mark.asyncio
    async def test_error_recovery_during_operation(self, temp_log_dir, mock_redis_client):
        """Test logger recovery from various error conditions"""
        client, pubsub = mock_redis_client
        
        logger = MailboxLogger(
            redis_url="redis://localhost:6379",
            log_directory=temp_log_dir,
            channel="test_channel"
        )
        
        # Simulate connection errors and recovery
        connection_attempts = 0
        
        async def mock_ping():
            nonlocal connection_attempts
            connection_attempts += 1
            if connection_attempts <= 2:
                raise redis.ConnectionError("Connection failed")
            # Succeed on third attempt
        
        client.ping = mock_ping
        
        # Test messages with some invalid JSON
        test_data = [
            '{"type": "simple_message", "source": "agent_1", "payload": {}}',  # Valid
            'invalid json {',  # Invalid JSON
            '{"type": "invalid_type", "source": "agent_2"}',  # Invalid message
            '{"type": "simple_message", "source": "agent_3", "payload": {"content": "valid"}}'  # Valid
        ]
        
        async def mock_listen():
            for data in test_data:
                yield {
                    'type': 'message',
                    'channel': 'test_channel',
                    'data': data
                }
                await asyncio.sleep(0.01)
        
        pubsub.listen = mock_listen
        
        with patch('redis.asyncio.from_url', return_value=client):
            # Start logger (will fail first few connection attempts)
            await logger.start_logging()
            
            # Wait for processing
            await asyncio.sleep(0.1)
            
            # Stop logger
            await logger.stop_logging()
        
        # Verify error handling
        assert logger.stats['messages_logged'] == 4  # All messages logged
        assert logger.stats['parsing_errors'] == 2  # Two parsing errors
        assert logger.stats['connection_errors'] == 2  # Two connection errors
        
        # Verify that valid messages were parsed correctly
        messages = await logger.check_mail()
        valid_messages = [msg for msg in messages if msg['message'] is not None]
        assert len(valid_messages) == 2  # Two valid messages
    
    @pytest.mark.asyncio
    async def test_mail_checking_with_large_history(self, temp_log_dir):
        """Test mail checking performance with large message history"""
        logger = MailboxLogger(log_directory=temp_log_dir)
        
        # Create multiple log files with many messages
        log_dir = Path(temp_log_dir)
        
        total_messages = 0
        for file_idx in range(3):
            log_file = log_dir / f"mailbox_test_{file_idx}.log"
            
            log_entries = []
            for msg_idx in range(100):
                message = BeastModeMessage(
                    type=MessageType.SIMPLE_MESSAGE,
                    source=f"agent_{msg_idx % 10}",
                    payload={"content": f"Message {msg_idx} in file {file_idx}"}
                )
                
                log_entry = {
                    'timestamp': (datetime.now() - timedelta(hours=file_idx, minutes=msg_idx)).isoformat(),
                    'channel': 'test_channel',
                    'raw_data': json.dumps(message.model_dump(), default=str),
                    'parsed_message': message.model_dump(),
                    'parsing_error': None
                }
                
                log_entries.append(json.dumps(log_entry, default=str))
                total_messages += 1
            
            log_file.write_text('\n'.join(log_entries))
        
        # Test various mail checking scenarios
        
        # Check all messages
        all_messages = await logger.check_mail()
        assert len(all_messages) == total_messages
        
        # Check with limit
        limited_messages = await logger.check_mail(limit=50)
        assert len(limited_messages) == 50
        
        # Check with time filter
        since_time = datetime.now() - timedelta(hours=1)
        recent_messages = await logger.check_mail(since=since_time)
        assert len(recent_messages) < total_messages
        
        # Check with source filter
        agent_messages = await logger.check_mail(source_agents=['agent_0', 'agent_1'])
        assert len(agent_messages) > 0
        assert all(msg['message']['source'] in ['agent_0', 'agent_1'] for msg in agent_messages)
        
        # Check with message type filter
        simple_messages = await logger.check_mail(message_types=[MessageType.SIMPLE_MESSAGE])
        assert len(simple_messages) == total_messages  # All are simple messages
    
    def test_manager_lifecycle_integration(self, temp_log_dir):
        """Test MailboxLoggerManager complete lifecycle"""
        manager = MailboxLoggerManager(
            log_directory=temp_log_dir,
            channel="test_channel"
        )
        
        # Test context manager usage
        with patch.object(manager.logger, 'start_logging') as mock_start:
            with patch.object(manager.logger, 'stop_logging') as mock_stop:
                with patch('threading.Thread') as mock_thread:
                    mock_thread_instance = MagicMock()
                    mock_thread_instance.is_alive.return_value = True
                    mock_thread.return_value = mock_thread_instance
                    
                    with manager:
                        # Manager should be running
                        assert manager.is_running
                        
                        # Check status
                        status = manager.get_status()
                        assert status['manager_running'] == True
                    
                    # After context exit, should be stopped
                    assert not manager.is_running
    
    @pytest.mark.asyncio
    async def test_concurrent_logging_and_reading(self, temp_log_dir, mock_redis_client):
        """Test concurrent logging and mail reading operations"""
        client, pubsub = mock_redis_client
        
        logger = MailboxLogger(
            redis_url="redis://localhost:6379",
            log_directory=temp_log_dir,
            channel="test_channel"
        )
        
        # Create a continuous stream of messages
        message_counter = 0
        
        async def mock_listen():
            nonlocal message_counter
            while logger.is_running:
                message = BeastModeMessage(
                    type=MessageType.SIMPLE_MESSAGE,
                    source=f"agent_{message_counter % 5}",
                    payload={"content": f"Concurrent message {message_counter}"}
                )
                
                redis_message = {
                    'type': 'message',
                    'channel': 'test_channel',
                    'data': json.dumps(message.model_dump(), default=str)
                }
                
                message_counter += 1
                yield redis_message
                await asyncio.sleep(0.01)
        
        pubsub.listen = mock_listen
        
        with patch('redis.asyncio.from_url', return_value=client):
            # Start logger
            await logger.start_logging()
            
            # Concurrently read mail while logging is happening
            read_tasks = []
            for _ in range(5):
                task = asyncio.create_task(logger.check_mail(limit=10))
                read_tasks.append(task)
                await asyncio.sleep(0.02)  # Stagger the reads
            
            # Wait for some messages to be logged
            await asyncio.sleep(0.2)
            
            # Collect read results
            read_results = await asyncio.gather(*read_tasks, return_exceptions=True)
            
            # Stop logger
            await logger.stop_logging()
        
        # Verify no exceptions occurred during concurrent operations
        for result in read_results:
            assert not isinstance(result, Exception)
        
        # Verify messages were logged
        assert logger.stats['messages_logged'] > 0
        
        # Verify final mail check works
        final_messages = await logger.check_mail()
        assert len(final_messages) == logger.stats['messages_logged']