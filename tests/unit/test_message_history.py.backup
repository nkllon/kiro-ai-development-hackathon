"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:24:55.610552
"""





import asyncio
import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from src.beast_mode.messaging.message_history import (
    MessageHistoryManager,
    MessageFilter,
    MessageEntry,
    MessageStatus,
    SortOrder
)
from src.beast_mode.messaging.models import BeastModeMessage, MessageType
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule



@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_messages():
    """Create sample messages for testing"""
    now = datetime.now()
    
    messages = [
        BeastModeMessage(
            id="msg-001",
            type=MessageType.SIMPLE_MESSAGE,
            source="agent-1",
            target="agent-2",
            payload={"text": "Hello world"},
            timestamp=now - timedelta(hours=2),
            priority=5
        ),
        BeastModeMessage(
            id="msg-002",
            type=MessageType.HELP_WANTED,
            source="agent-2",
            target="agent-1",
            payload={"help_type": "coding", "description": "Need help with Python"},
            timestamp=now - timedelta(hours=1),
            priority=3,
            correlation_id="conv-001"
        ),
        BeastModeMessage(
            id="msg-003",
            type=MessageType.HELP_RESPONSE,
            source="agent-1",
            target="agent-2",
            payload={"response": "I can help with Python"},
            timestamp=now - timedelta(minutes=30),
            priority=3,
            correlation_id="conv-001"
        ),
        BeastModeMessage(
            id="msg-004",
            type=MessageType.SYSTEM_HEALTH,
            source="agent-3",
            target=None,  # Broadcast
            payload={"status": "healthy", "cpu": 25.5},
            timestamp=now - timedelta(minutes=10),
            priority=7
        )
    ]
    
    return messages


@pytest.fixture
def sample_log_entries(sample_messages):
    """Create sample log entries"""
    entries = []
    
    for i, message in enumerate(sample_messages):
        entry = {
            'timestamp': message.timestamp.isoformat(),
            'channel': 'beast_mode_network',
            'raw_data': message.model_dump_json(),
            'parsed_message': message.model_dump(),
            'parsing_error': None
        }
        entries.append(entry)
    
    return entries


@pytest.fixture
async def history_manager(temp_log_dir):
    """Create a message history manager for testing"""
    manager = MessageHistoryManager(
        log_directory=temp_log_dir,
        auto_save_interval=1  # Fast auto-save for testing
    )
    
    await manager.start()
    yield manager
    await manager.stop()


class TestMessageFilter(ReflectiveModule):
    """Test MessageFilter functionality"""
    
    def test_default_filter(self):
        """Test default filter creation"""
        filter_criteria = MessageFilter()
        
        assert filter_criteria.since is None
        assert filter_criteria.until is None
        assert filter_criteria.message_types is None
        assert filter_criteria.source_agents is None
        assert filter_criteria.target_agents is None
        assert filter_criteria.status is None
        assert filter_criteria.priority_min is None
        assert filter_criteria.priority_max is None
        assert filter_criteria.search_text is None
        assert filter_criteria.correlation_ids is None
        assert filter_criteria.limit is None
        assert filter_criteria.offset == 0
    
    def test_filter_with_criteria(self):
        """Test filter with specific criteria"""
        since = datetime.now() - timedelta(hours=1)
        until = datetime.now()
        
        filter_criteria = MessageFilter(
            since=since,
            until=until,
            message_types=[MessageType.SIMPLE_MESSAGE, MessageType.HELP_WANTED],
            source_agents=["agent-1"],
            target_agents=["agent-2"],
            status=[MessageStatus.UNREAD],
            priority_min=1,
            priority_max=5,
            search_text="hello",
            correlation_ids=["conv-001"],
            limit=10,
            offset=5
        )
        
        assert filter_criteria.since == since
        assert filter_criteria.until == until
        assert MessageType.SIMPLE_MESSAGE in filter_criteria.message_types
        assert MessageType.HELP_WANTED in filter_criteria.message_types
        assert "agent-1" in filter_criteria.source_agents
        assert "agent-2" in filter_criteria.target_agents
        assert MessageStatus.UNREAD in filter_criteria.status
        assert filter_criteria.priority_min == 1
        assert filter_criteria.priority_max == 5
        assert filter_criteria.search_text == "hello"
        assert "conv-001" in filter_criteria.correlation_ids
        assert filter_criteria.limit == 10
        assert filter_criteria.offset == 5


class TestMessageEntry(ReflectiveModule):
    """Test MessageEntry functionality"""
    
    def test_message_entry_creation(self, sample_messages):
        """Test creating a message entry"""
        message = sample_messages[0]
        log_timestamp = datetime.now()
        
        entry = MessageEntry(
            log_timestamp=log_timestamp,
            message=message,
            log_file="/path/to/log.log",
            status=MessageStatus.READ,
            read_timestamp=datetime.now(),
            tags={"important", "work"},
            notes="This is a test message"
        )
        
        assert entry.log_timestamp == log_timestamp
        assert entry.message == message
        assert entry.log_file == "/path/to/log.log"
        assert entry.status == MessageStatus.READ
        assert entry.read_timestamp is not None
        assert "important" in entry.tags
        assert "work" in entry.tags
        assert entry.notes == "This is a test message"
    
    def test_message_entry_defaults(self, sample_messages):
        """Test message entry with default values"""
        message = sample_messages[0]
        log_timestamp = datetime.now()
        
        entry = MessageEntry(
            log_timestamp=log_timestamp,
            message=message,
            log_file="/path/to/log.log"
        )
        
        assert entry.status == MessageStatus.UNREAD
        assert entry.read_timestamp is None
        assert len(entry.tags) == 0
        assert entry.notes is None


class TestMessageHistoryManager(ReflectiveModule):
    """Test MessageHistoryManager functionality"""
    
    def test_initialization(self, temp_log_dir):
        """Test manager initialization"""
        manager = MessageHistoryManager(log_directory=temp_log_dir)
        
        assert manager.log_directory == Path(temp_log_dir)
        assert manager.status_file == Path(temp_log_dir) / "message_status.json"
        assert manager.cache_size == 1000
        assert manager.auto_save_interval == 300
        assert not manager.is_running
        assert len(manager.message_status) == 0
        assert len(manager.message_cache) == 0
    
    async def test_start_stop(self, temp_log_dir):
        """Test starting and stopping the manager"""
        manager = MessageHistoryManager(log_directory=temp_log_dir)
        
        assert not manager.is_running
        
        await manager.start()
        assert manager.is_running
        assert manager.auto_save_task is not None
        
        await manager.stop()
        assert not manager.is_running
        assert manager.auto_save_task.done()
    
    def test_create_log_files(self, temp_log_dir, sample_log_entries):
        """Create sample log files for testing"""
        log_dir = Path(temp_log_dir)
        
        # Create first log file
        log_file_1 = log_dir / "mailbox_20240101_120000.log"
        with open(log_file_1, 'w', encoding='utf-8') as f:
            for entry in sample_log_entries[:2]:
                f.write(json.dumps(entry, default=str) + '\n')
        
        # Create second log file
        log_file_2 = log_dir / "mailbox_20240101_130000.log"
        with open(log_file_2, 'w', encoding='utf-8') as f:
            for entry in sample_log_entries[2:]:
                f.write(json.dumps(entry, default=str) + '\n')
        
        return [log_file_1, log_file_2]
    
    async def test_get_log_files(self, history_manager, sample_log_entries):
        """Test getting log file information"""
        # Create test log files
        log_files = self.test_create_log_files(
            str(history_manager.log_directory), 
            sample_log_entries
        )
        
        # Get log file info
        log_file_info = await history_manager._get_log_files()
        
        assert len(log_file_info) == 2
        
        # Check that files are sorted by creation time (newest first)
        assert "mailbox_20240101_130000.log" in log_file_info[0]['path']
        assert "mailbox_20240101_120000.log" in log_file_info[1]['path']
        
        # Check file info structure
        for info in log_file_info:
            assert 'path' in info
            assert 'size_bytes' in info
            assert 'created' in info
            assert 'modified' in info
    
    async def test_scan_log_file(self, history_manager, sample_log_entries):
        """Test scanning a single log file"""
        # Create test log file
        log_files = self.test_create_log_files(
            str(history_manager.log_directory), 
            sample_log_entries
        )
        
        # Scan the first log file
        filter_criteria = MessageFilter()
        messages = await history_manager._scan_log_file(log_files[0], filter_criteria)
        
        assert len(messages) == 2
        
        # Check message structure
        for message_entry in messages:
            assert isinstance(message_entry, MessageEntry)
            assert message_entry.message is not None
            assert message_entry.log_timestamp is not None
            assert message_entry.log_file == str(log_files[0])
            assert message_entry.status == MessageStatus.UNREAD
    
    async def test_scan_messages_no_filter(self, history_manager, sample_log_entries):
        """Test scanning messages without filters"""
        # Create test log files
        self.test_create_log_files(
            str(history_manager.log_directory), 
            sample_log_entries
        )
        
        # Scan all messages
        messages = await history_manager.scan_messages()
        
        assert len(messages) == 4
        
        # Check that messages are sorted by timestamp (newest first by default)
        timestamps = [msg.log_timestamp for msg in messages]
        assert timestamps == sorted(timestamps, reverse=True)
    
    async def test_scan_messages_with_filters(self, history_manager, sample_log_entries):
        """Test scanning messages with various filters"""
        # Create test log files
        self.test_create_log_files(
            str(history_manager.log_directory), 
            sample_log_entries
        )
        
        # Test message type filter
        filter_criteria = MessageFilter(
            message_types=[MessageType.HELP_WANTED, MessageType.HELP_RESPONSE]
        )
        messages = await history_manager.scan_messages(filter_criteria)
        assert len(messages) == 2
        
        # Test source agent filter
        filter_criteria = MessageFilter(source_agents=["agent-1"])
        messages = await history_manager.scan_messages(filter_criteria)
        assert len(messages) == 2
        
        # Test target agent filter
        filter_criteria = MessageFilter(target_agents=["agent-2"])
        messages = await history_manager.scan_messages(filter_criteria)
        assert len(messages) == 3  # Including broadcast messages
        
        # Test priority filter
        filter_criteria = MessageFilter(priority_min=1, priority_max=5)
        messages = await history_manager.scan_messages(filter_criteria)
        assert len(messages) == 3
        
        # Test correlation ID filter
        filter_criteria = MessageFilter(correlation_ids=["conv-001"])
        messages = await history_manager.scan_messages(filter_criteria)
        assert len(messages) == 2
        
        # Test search text filter
        filter_criteria = MessageFilter(search_text="Python")
        messages = await history_manager.scan_messages(filter_criteria)
        assert len(messages) == 2  # Both help messages mention Python
        
        # Test limit and offset
        filter_criteria = MessageFilter(limit=2, offset=1)
        messages = await history_manager.scan_messages(filter_criteria)
        assert len(messages) == 2
    
    async def test_check_mail(self, history_manager, sample_log_entries):
        """Test checking mail for a specific agent"""
        # Create test log files
        self.test_create_log_files(
            str(history_manager.log_directory), 
            sample_log_entries
        )
        
        # Check mail for agent-2
        messages = await history_manager.check_mail("agent-2", mark_as_read=False)
        
        # Should get 3 messages (2 targeted + 1 broadcast)
        assert len(messages) == 3
        
        # All messages should be unread since we didn't mark as read
        for message_entry in messages:
            assert message_entry.status == MessageStatus.UNREAD
        
        # Check mail and mark as read
        messages = await history_manager.check_mail("agent-2", mark_as_read=True)
        
        # Verify messages are marked as read
        for message_entry in messages:
            status_data = history_manager.message_status.get(message_entry.message.id, {})
            assert status_data.get('status') == MessageStatus.READ.value
    
    async def test_search_messages(self, history_manager, sample_log_entries):
        """Test searching messages by text"""
        # Create test log files
        self.test_create_log_files(
            str(history_manager.log_directory), 
            sample_log_entries
        )
        
        # Search for "Python"
        messages = await history_manager.search_messages("Python")
        assert len(messages) == 2
        
        # Search for "hello" (case insensitive)
        messages = await history_manager.search_messages("hello")
        assert len(messages) == 1
        
        # Search with agent filter
        messages = await history_manager.search_messages("help", agent_id="agent-2")
        assert len(messages) == 2
        
        # Search with message type filter
        messages = await history_manager.search_messages(
            "help", 
            message_types=[MessageType.HELP_WANTED]
        )
        assert len(messages) == 1
    
    async def test_get_conversation_thread(self, history_manager, sample_log_entries):
        """Test getting conversation thread by correlation ID"""
        # Create test log files
        self.test_create_log_files(
            str(history_manager.log_directory), 
            sample_log_entries
        )
        
        # Get conversation thread
        messages = await history_manager.get_conversation_thread("conv-001")
        
        assert len(messages) == 2
        
        # Messages should be sorted by timestamp (oldest first for conversation)
        assert messages[0].message.type == MessageType.HELP_WANTED
        assert messages[1].message.type == MessageType.HELP_RESPONSE
    
    async def test_message_status_operations(self, history_manager):
        """Test message status operations"""
        message_id = "test-msg-001"
        
        # Mark as read
        await history_manager.mark_message_read(message_id)
        status_data = history_manager.message_status[message_id]
        assert status_data['status'] == MessageStatus.READ.value
        assert 'read_timestamp' in status_data
        
        # Mark as unread
        await history_manager.mark_message_unread(message_id)
        status_data = history_manager.message_status[message_id]
        assert status_data['status'] == MessageStatus.UNREAD.value
        assert 'read_timestamp' not in status_data
        
        # Archive message
        await history_manager.archive_message(message_id)
        status_data = history_manager.message_status[message_id]
        assert status_data['status'] == MessageStatus.ARCHIVED.value
        
        # Flag message
        await history_manager.flag_message(message_id)
        status_data = history_manager.message_status[message_id]
        assert status_data['status'] == MessageStatus.FLAGGED.value
    
    async def test_message_tags_and_notes(self, history_manager):
        """Test adding tags and notes to messages"""
        message_id = "test-msg-002"
        
        # Add tags
        await history_manager.add_message_tag(message_id, "important")
        await history_manager.add_message_tag(message_id, "work")
        
        status_data = history_manager.message_status[message_id]
        assert "important" in status_data['tags']
        assert "work" in status_data['tags']
        
        # Remove tag
        await history_manager.remove_message_tag(message_id, "work")
        status_data = history_manager.message_status[message_id]
        assert "important" in status_data['tags']
        assert "work" not in status_data['tags']
        
        # Add note
        await history_manager.add_message_note(message_id, "This is a test note")
        status_data = history_manager.message_status[message_id]
        assert status_data['notes'] == "This is a test note"
    
    async def test_get_message_counts(self, history_manager, sample_log_entries):
        """Test getting message counts by status"""
        # Create test log files
        self.test_create_log_files(
            str(history_manager.log_directory), 
            sample_log_entries
        )
        
        # Mark some messages as read
        await history_manager.mark_message_read("msg-001")
        await history_manager.mark_message_read("msg-002")
        await history_manager.archive_message("msg-003")
        
        # Get counts for agent-2
        counts = await history_manager.get_message_counts(agent_id="agent-2")
        
        assert counts['total'] == 3  # 2 targeted + 1 broadcast
        assert counts[MessageStatus.READ.value] == 2
        assert counts[MessageStatus.ARCHIVED.value] == 1
        assert counts[MessageStatus.UNREAD.value] == 0
    
    async def test_status_persistence(self, temp_log_dir):
        """Test that message status is persisted and loaded"""
        # Create manager and add some status
        manager1 = MessageHistoryManager(log_directory=temp_log_dir)
        await manager1.start()
        
        await manager1.mark_message_read("msg-001")
        await manager1.add_message_tag("msg-001", "important")
        await manager1.add_message_note("msg-001", "Test note")
        
        # Force save
        await manager1._save_status_data()
        await manager1.stop()
        
        # Create new manager and verify status is loaded
        manager2 = MessageHistoryManager(log_directory=temp_log_dir)
        
        status_data = manager2.message_status.get("msg-001", {})
        assert status_data['status'] == MessageStatus.READ.value
        assert "important" in status_data['tags']
        assert status_data['notes'] == "Test note"
    
    async def test_cleanup_old_status(self, history_manager, sample_log_entries):
        """Test cleaning up old message status"""
        # Create test log files
        self.test_create_log_files(
            str(history_manager.log_directory), 
            sample_log_entries
        )
        
        # Add status for existing and non-existing messages
        await history_manager.mark_message_read("msg-001")  # Exists
        await history_manager.mark_message_read("msg-999")  # Doesn't exist
        
        assert len(history_manager.message_status) == 2
        
        # Cleanup old status
        removed_count = await history_manager.cleanup_old_status(days_old=0)
        
        # Should remove status for non-existing message
        assert removed_count == 1
        assert "msg-001" in history_manager.message_status
        assert "msg-999" not in history_manager.message_status
    
    def test_message_contains_text(self, history_manager, sample_messages):
        """Test text search functionality"""
        message = sample_messages[1]  # Help wanted message
        
        # Test case insensitive search
        assert history_manager._message_contains_text(message, "python")
        assert history_manager._message_contains_text(message, "PYTHON")
        assert history_manager._message_contains_text(message, "Python")
        
        # Test search in different fields
        assert history_manager._message_contains_text(message, "agent-2")  # source
        assert history_manager._message_contains_text(message, "coding")   # payload
        assert history_manager._message_contains_text(message, "help_wanted")  # type
        
        # Test non-matching search
        assert not history_manager._message_contains_text(message, "nonexistent")
    
    def test_message_matches_filter(self, history_manager, sample_messages):
        """Test message filter matching"""
        message = sample_messages[1]  # Help wanted message
        log_timestamp = message.timestamp
        
        message_entry = MessageEntry(
            log_timestamp=log_timestamp,
            message=message,
            log_file="/test/log.log",
            status=MessageStatus.UNREAD
        )
        
        # Test time range filter
        filter_criteria = MessageFilter(
            since=message.timestamp - timedelta(minutes=30),
            until=message.timestamp + timedelta(minutes=30)
        )
        assert history_manager._message_matches_filter(message_entry, filter_criteria)
        
        filter_criteria = MessageFilter(
            since=message.timestamp + timedelta(minutes=30)
        )
        assert not history_manager._message_matches_filter(message_entry, filter_criteria)
        
        # Test message type filter
        filter_criteria = MessageFilter(
            message_types=[MessageType.HELP_WANTED]
        )
        assert history_manager._message_matches_filter(message_entry, filter_criteria)
        
        filter_criteria = MessageFilter(
            message_types=[MessageType.SIMPLE_MESSAGE]
        )
        assert not history_manager._message_matches_filter(message_entry, filter_criteria)
        
        # Test agent filters
        filter_criteria = MessageFilter(source_agents=["agent-2"])
        assert history_manager._message_matches_filter(message_entry, filter_criteria)
        
        filter_criteria = MessageFilter(source_agents=["agent-3"])
        assert not history_manager._message_matches_filter(message_entry, filter_criteria)
        
        # Test priority filter
        filter_criteria = MessageFilter(priority_min=1, priority_max=5)
        assert history_manager._message_matches_filter(message_entry, filter_criteria)
        
        filter_criteria = MessageFilter(priority_min=8, priority_max=10)
        assert not history_manager._message_matches_filter(message_entry, filter_criteria)
    
    def test_get_stats(self, history_manager):
        """Test getting manager statistics"""
        stats = history_manager.get_stats()
        
        assert 'messages_scanned' in stats
        assert 'cache_hits' in stats
        assert 'cache_misses' in stats
        assert 'status_updates' in stats
        assert 'searches_performed' in stats
        assert 'is_running' in stats
        assert 'message_status_count' in stats
        assert 'cache_size' in stats
        assert 'status_dirty' in stats
        assert 'log_directory' in stats
    
    def test_get_health_status(self, history_manager):
        """Test getting health status"""
        health = history_manager.get_health_status()
        
        assert 'status' in health
        assert 'is_running' in health
        assert 'log_directory' in health
        assert 'status_file' in health
        assert 'stats' in health
        
        assert health['status'] in ["healthy", "stopped"]
        assert health['is_running'] == history_manager.is_running


@pytest.mark.asyncio
class TestMessageHistoryIntegration(ReflectiveModule):
    """Integration tests for message history functionality"""
    
    async def test_full_workflow(self, temp_log_dir, sample_messages, sample_log_entries):
        """Test complete message history workflow"""
        # Create manager
        manager = MessageHistoryManager(log_directory=temp_log_dir)
        await manager.start()
        
        try:
            # Create test log files
            log_dir = Path(temp_log_dir)
            log_file = log_dir / "mailbox_test.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                for entry in sample_log_entries:
                    f.write(json.dumps(entry, default=str) + '\n')
            
            # Scan messages
            messages = await manager.scan_messages()
            assert len(messages) == 4
            
            # Check mail for specific agent
            agent_messages = await manager.check_mail("agent-2", mark_as_read=True)
            assert len(agent_messages) == 3
            
            # Search messages
            search_results = await manager.search_messages("Python")
            assert len(search_results) == 2
            
            # Get conversation thread
            thread = await manager.get_conversation_thread("conv-001")
            assert len(thread) == 2
            
            # Add tags and notes
            await manager.add_message_tag("msg-001", "important")
            await manager.add_message_note("msg-001", "Test note")
            
            # Get message counts
            counts = await manager.get_message_counts("agent-2")
            assert counts['total'] == 3
            assert counts[MessageStatus.READ.value] == 3
            
            # Verify status persistence
            await manager._save_status_data()
            
            # Check stats
            stats = manager.get_stats()
            assert stats['messages_scanned'] > 0
            assert stats['searches_performed'] > 0
            assert stats['status_updates'] > 0
            
        finally:

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

            await manager.stop()