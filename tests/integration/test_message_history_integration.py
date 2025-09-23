"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.565008
"""




import asyncio
import json
import pytest
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch

from src.beast_mode.messaging.message_history import (
    MessageHistoryManager,
    MessageFilter,
    MessageStatus
)
from src.beast_mode.messaging.mailbox_logger import MailboxLogger
from src.beast_mode.messaging.models import BeastModeMessage, MessageType


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
            id="integration-msg-001",
            type=MessageType.SIMPLE_MESSAGE,
            source="integration-agent-1",
            target="integration-agent-2",
            payload={"text": "Integration test message 1"},
            timestamp=now - timedelta(hours=2),
            priority=5
        ),
        BeastModeMessage(
            id="integration-msg-002",
            type=MessageType.HELP_WANTED,
            source="integration-agent-2",
            target="integration-agent-1",
            payload={
                "help_type": "integration_testing",
                "description": "Need help with integration tests"
            },
            timestamp=now - timedelta(hours=1),
            priority=3,
            correlation_id="integration-conv-001"
        ),
        BeastModeMessage(
            id="integration-msg-003",
            type=MessageType.HELP_RESPONSE,
            source="integration-agent-1",
            target="integration-agent-2",
            payload={"response": "I can help with integration testing"},
            timestamp=now - timedelta(minutes=30),
            priority=3,
            correlation_id="integration-conv-001"
        ),
        BeastModeMessage(
            id="integration-msg-004",
            type=MessageType.SYSTEM_HEALTH,
            source="integration-agent-3",
            target=None,  # Broadcast
            payload={"status": "healthy", "memory_usage": 45.2},
            timestamp=now - timedelta(minutes=10),
            priority=7
        ),
        BeastModeMessage(
            id="integration-msg-005",
            type=MessageType.SPORE_DELIVERY,
            source="integration-agent-1",
            target="integration-agent-2",
            payload={
                "spore_name": "test_optimization",
                "spore_content": "def optimize(): return 'optimized'"
            },
            timestamp=now - timedelta(minutes=5),
            priority=4
        )
    ]
    
    return messages


class TestMessageHistoryIntegration(ReflectiveModule):
    """Integration tests for message history functionality"""
    
    async def test_history_with_real_log_files(self, temp_log_dir, sample_messages):
        """Test message history with real log files created by mailbox logger"""
        # Create mailbox logger to generate real log files
        logger = MailboxLogger(
            redis_url="redis://localhost:6379",
            log_directory=temp_log_dir,
            max_log_size_mb=1  # Small size for testing rotation
        )
        
        # Create history manager
        history_manager = MessageHistoryManager(log_directory=temp_log_dir)
        await history_manager.start()
        
        try:
            # Simulate log entries by directly writing to log files
            # (since we don't want to depend on Redis for unit tests)
            log_dir = Path(temp_log_dir)
            log_file = log_dir / "mailbox_integration_test.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                for message in sample_messages:
                    log_entry = {
                        'timestamp': message.timestamp.isoformat(),
                        'channel': 'beast_mode_network',
                        'raw_data': message.model_dump_json(),
                        'parsed_message': message.model_dump(),
                        'parsing_error': None
                    }
                    f.write(json.dumps(log_entry, default=str) + '\n')
            
            # Test scanning all messages
            all_messages = await history_manager.scan_messages()
            assert len(all_messages) == 5
            
            # Verify message order (newest first by default)
            timestamps = [msg.log_timestamp for msg in all_messages]
            assert timestamps == sorted(timestamps, reverse=True)
            
            # Test filtering by message type
            help_messages = await history_manager.scan_messages(
                MessageFilter(message_types=[MessageType.HELP_WANTED, MessageType.HELP_RESPONSE])
            )
            assert len(help_messages) == 2
            
            # Test filtering by agent
            agent_2_messages = await history_manager.scan_messages(
                MessageFilter(target_agents=["integration-agent-2"])
            )
            assert len(agent_2_messages) == 4  # 3 targeted + 1 broadcast
            
            # Test time-based filtering
            recent_messages = await history_manager.scan_messages(
                MessageFilter(since=datetime.now() - timedelta(hours=1))
            )
            assert len(recent_messages) == 3
            
        finally:
            await history_manager.stop()
    
    async def test_check_mail_workflow(self, temp_log_dir, sample_messages):
        """Test complete check mail workflow"""
        history_manager = MessageHistoryManager(log_directory=temp_log_dir)
        await history_manager.start()
        
        try:
            # Create log file with messages
            log_dir = Path(temp_log_dir)
            log_file = log_dir / "mailbox_check_mail_test.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                for message in sample_messages:
                    log_entry = {
                        'timestamp': message.timestamp.isoformat(),
                        'channel': 'beast_mode_network',
                        'raw_data': message.model_dump_json(),
                        'parsed_message': message.model_dump(),
                        'parsing_error': None
                    }
                    f.write(json.dumps(log_entry, default=str) + '\n')
            
            # Check mail for integration-agent-2 (should get 4 messages)
            messages = await history_manager.check_mail(
                "integration-agent-2",
                mark_as_read=False
            )
            assert len(messages) == 4
            
            # All messages should be unread
            for msg in messages:
                assert msg.status == MessageStatus.UNREAD
            
            # Check mail again and mark as read
            messages = await history_manager.check_mail(
                "integration-agent-2",
                mark_as_read=True
            )
            assert len(messages) == 4
            
            # Verify messages are marked as read in status tracking
            for msg in messages:
                status_data = history_manager.message_status.get(msg.message.id, {})
                assert status_data.get('status') == MessageStatus.READ.value
                assert 'read_timestamp' in status_data
            
            # Check mail again - should get same messages but marked as read
            messages = await history_manager.check_mail(
                "integration-agent-2",
                mark_as_read=False
            )
            assert len(messages) == 4
            
            # Messages should now show as read
            for msg in messages:
                assert msg.status == MessageStatus.READ
                assert msg.read_timestamp is not None
            
        finally:
            await history_manager.stop()
    
    async def test_conversation_threading(self, temp_log_dir, sample_messages):
        """Test conversation threading functionality"""
        history_manager = MessageHistoryManager(log_directory=temp_log_dir)
        await history_manager.start()
        
        try:
            # Create log file with messages
            log_dir = Path(temp_log_dir)
            log_file = log_dir / "mailbox_conversation_test.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                for message in sample_messages:
                    log_entry = {
                        'timestamp': message.timestamp.isoformat(),
                        'channel': 'beast_mode_network',
                        'raw_data': message.model_dump_json(),
                        'parsed_message': message.model_dump(),
                        'parsing_error': None
                    }
                    f.write(json.dumps(log_entry, default=str) + '\n')
            
            # Get conversation thread
            thread = await history_manager.get_conversation_thread("integration-conv-001")
            
            assert len(thread) == 2
            
            # Messages should be in chronological order (oldest first)
            assert thread[0].message.type == MessageType.HELP_WANTED
            assert thread[1].message.type == MessageType.HELP_RESPONSE
            
            # Verify correlation IDs match
            for msg in thread:
                assert msg.message.correlation_id == "integration-conv-001"
            
            # Test non-existent conversation
            empty_thread = await history_manager.get_conversation_thread("non-existent")
            assert len(empty_thread) == 0
            
        finally:
            await history_manager.stop()
    
    async def test_search_functionality(self, temp_log_dir, sample_messages):
        """Test message search functionality"""
        history_manager = MessageHistoryManager(log_directory=temp_log_dir)
        await history_manager.start()
        
        try:
            # Create log file with messages
            log_dir = Path(temp_log_dir)
            log_file = log_dir / "mailbox_search_test.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                for message in sample_messages:
                    log_entry = {
                        'timestamp': message.timestamp.isoformat(),
                        'channel': 'beast_mode_network',
                        'raw_data': message.model_dump_json(),
                        'parsed_message': message.model_dump(),
                        'parsing_error': None
                    }
                    f.write(json.dumps(log_entry, default=str) + '\n')
            
            # Search for "integration" (should match multiple messages)
            results = await history_manager.search_messages("integration")
            assert len(results) >= 3  # At least the help messages and simple message
            
            # Search for "testing" (case insensitive)
            results = await history_manager.search_messages("testing")
            assert len(results) == 2  # Help wanted and response
            
            # Search with agent filter
            results = await history_manager.search_messages(
                "integration",
                agent_id="integration-agent-2"
            )
            assert len(results) >= 2
            
            # Search with message type filter
            results = await history_manager.search_messages(
                "help",
                message_types=[MessageType.HELP_WANTED]
            )
            assert len(results) == 1
            
            # Search with time filter
            recent_time = datetime.now() - timedelta(hours=1)
            results = await history_manager.search_messages(
                "integration",
                since=recent_time
            )
            assert len(results) >= 2  # Recent messages only
            
            # Search with limit
            results = await history_manager.search_messages(
                "integration",
                limit=2
            )
            assert len(results) == 2
            
        finally:
            await history_manager.stop()
    
    async def test_message_status_management(self, temp_log_dir, sample_messages):
        """Test comprehensive message status management"""
        history_manager = MessageHistoryManager(log_directory=temp_log_dir)
        await history_manager.start()
        
        try:
            # Create log file with messages
            log_dir = Path(temp_log_dir)
            log_file = log_dir / "mailbox_status_test.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                for message in sample_messages:
                    log_entry = {
                        'timestamp': message.timestamp.isoformat(),
                        'channel': 'beast_mode_network',
                        'raw_data': message.model_dump_json(),
                        'parsed_message': message.model_dump(),
                        'parsing_error': None
                    }
                    f.write(json.dumps(log_entry, default=str) + '\n')
            
            # Get initial message counts
            counts = await history_manager.get_message_counts("integration-agent-2")
            assert counts['total'] == 4
            assert counts[MessageStatus.UNREAD.value] == 4
            assert counts[MessageStatus.READ.value] == 0
            
            # Mark some messages as read
            await history_manager.mark_message_read("integration-msg-001")
            await history_manager.mark_message_read("integration-msg-002")
            
            # Archive one message
            await history_manager.archive_message("integration-msg-003")
            
            # Flag one message
            await history_manager.flag_message("integration-msg-005")
            
            # Add tags to messages
            await history_manager.add_message_tag("integration-msg-001", "important")
            await history_manager.add_message_tag("integration-msg-001", "work")
            await history_manager.add_message_tag("integration-msg-002", "help")
            
            # Add notes to messages
            await history_manager.add_message_note(
                "integration-msg-001", 
                "This is an important integration test message"
            )
            await history_manager.add_message_note(
                "integration-msg-002",
                "Help request for integration testing"
            )
            
            # Get updated message counts
            counts = await history_manager.get_message_counts("integration-agent-2")
            assert counts['total'] == 4
            assert counts[MessageStatus.UNREAD.value] == 1  # Only broadcast message
            assert counts[MessageStatus.READ.value] == 2
            assert counts[MessageStatus.ARCHIVED.value] == 1
            assert counts[MessageStatus.FLAGGED.value] == 1
            
            # Test filtering by status
            read_messages = await history_manager.scan_messages(
                MessageFilter(
                    target_agents=["integration-agent-2"],
                    status=[MessageStatus.READ]
                )
            )
            assert len(read_messages) == 2
            
            flagged_messages = await history_manager.scan_messages(
                MessageFilter(
                    target_agents=["integration-agent-2"],
                    status=[MessageStatus.FLAGGED]
                )
            )
            assert len(flagged_messages) == 1
            
            # Verify tags and notes are preserved
            all_messages = await history_manager.scan_messages(
                MessageFilter(target_agents=["integration-agent-2"])
            )
            
            for msg in all_messages:
                if msg.message.id == "integration-msg-001":
                    assert "important" in msg.tags
                    assert "work" in msg.tags
                    assert "This is an important integration test message" in msg.notes
                elif msg.message.id == "integration-msg-002":
                    assert "help" in msg.tags
                    assert "Help request for integration testing" in msg.notes
            
        finally:
            await history_manager.stop()
    
    async def test_status_persistence_across_restarts(self, temp_log_dir, sample_messages):
        """Test that message status persists across manager restarts"""
        # First manager instance
        history_manager_1 = MessageHistoryManager(log_directory=temp_log_dir)
        await history_manager_1.start()
        
        try:
            # Create log file with messages
            log_dir = Path(temp_log_dir)
            log_file = log_dir / "mailbox_persistence_test.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                for message in sample_messages:
                    log_entry = {
                        'timestamp': message.timestamp.isoformat(),
                        'channel': 'beast_mode_network',
                        'raw_data': message.model_dump_json(),
                        'parsed_message': message.model_dump(),
                        'parsing_error': None
                    }
                    f.write(json.dumps(log_entry, default=str) + '\n')
            
            # Set various statuses
            await history_manager_1.mark_message_read("integration-msg-001")
            await history_manager_1.archive_message("integration-msg-002")
            await history_manager_1.flag_message("integration-msg-003")
            await history_manager_1.add_message_tag("integration-msg-001", "persistent")
            await history_manager_1.add_message_note("integration-msg-001", "Persistent note")
            
            # Force save status
            await history_manager_1._save_status_data()
            
        finally:
            await history_manager_1.stop()
        
        # Second manager instance (should load persisted status)
        history_manager_2 = MessageHistoryManager(log_directory=temp_log_dir)
        await history_manager_2.start()
        
        try:
            # Verify status was loaded
            assert len(history_manager_2.message_status) == 3
            
            # Check specific statuses
            msg_001_status = history_manager_2.message_status["integration-msg-001"]
            assert msg_001_status['status'] == MessageStatus.READ.value
            assert "persistent" in msg_001_status['tags']
            assert msg_001_status['notes'] == "Persistent note"
            
            msg_002_status = history_manager_2.message_status["integration-msg-002"]
            assert msg_002_status['status'] == MessageStatus.ARCHIVED.value
            
            msg_003_status = history_manager_2.message_status["integration-msg-003"]
            assert msg_003_status['status'] == MessageStatus.FLAGGED.value
            
            # Verify status is reflected in scanned messages
            messages = await history_manager_2.scan_messages()
            
            for msg in messages:
                if msg.message.id == "integration-msg-001":
                    assert msg.status == MessageStatus.READ
                    assert "persistent" in msg.tags
                    assert msg.notes == "Persistent note"
                elif msg.message.id == "integration-msg-002":
                    assert msg.status == MessageStatus.ARCHIVED
                elif msg.message.id == "integration-msg-003":
                    assert msg.status == MessageStatus.FLAGGED
            
        finally:
            await history_manager_2.stop()
    
    async def test_large_message_volume_performance(self, temp_log_dir):
        """Test performance with larger message volumes"""
        history_manager = MessageHistoryManager(log_directory=temp_log_dir)
        await history_manager.start()
        
        try:
            # Create log file with many messages
            log_dir = Path(temp_log_dir)
            log_file = log_dir / "mailbox_performance_test.log"
            
            num_messages = 1000
            base_time = datetime.now() - timedelta(hours=24)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                for i in range(num_messages):
                    message = BeastModeMessage(
                        id=f"perf-msg-{i:04d}",
                        type=MessageType.SIMPLE_MESSAGE,
                        source=f"agent-{i % 10}",
                        target=f"target-{i % 5}" if i % 3 != 0 else None,
                        payload={"text": f"Performance test message {i}"},
                        timestamp=base_time + timedelta(minutes=i),
                        priority=i % 10 + 1
                    )
                    
                    log_entry = {
                        'timestamp': message.timestamp.isoformat(),
                        'channel': 'beast_mode_network',
                        'raw_data': message.model_dump_json(),
                        'parsed_message': message.model_dump(),
                        'parsing_error': None
                    }
                    f.write(json.dumps(log_entry, default=str) + '\n')
            
            # Test scanning performance
            start_time = time.time()
            all_messages = await history_manager.scan_messages()
            scan_time = time.time() - start_time
            
            assert len(all_messages) == num_messages
            assert scan_time < 5.0  # Should complete within 5 seconds
            
            # Test filtered scanning performance
            start_time = time.time()
            filtered_messages = await history_manager.scan_messages(
                MessageFilter(
                    source_agents=["agent-1", "agent-2"],
                    priority_min=1,
                    priority_max=5,
                    limit=100
                )
            )
            filter_time = time.time() - start_time
            
            assert len(filtered_messages) == 100
            assert filter_time < 2.0  # Should complete within 2 seconds
            
            # Test search performance
            start_time = time.time()
            search_results = await history_manager.search_messages(
                "Performance test",
                limit=50
            )
            search_time = time.time() - start_time
            
            assert len(search_results) == 50
            assert search_time < 3.0  # Should complete within 3 seconds
            
        finally:
            await history_manager.stop()
    
    async def test_concurrent_access(self, temp_log_dir, sample_messages):
        """Test concurrent access to message history"""
        history_manager = MessageHistoryManager(log_directory=temp_log_dir)
        await history_manager.start()
        
        try:
            # Create log file with messages
            log_dir = Path(temp_log_dir)
            log_file = log_dir / "mailbox_concurrent_test.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                for message in sample_messages:
                    log_entry = {
                        'timestamp': message.timestamp.isoformat(),
                        'channel': 'beast_mode_network',
                        'raw_data': message.model_dump_json(),
                        'parsed_message': message.model_dump(),
                        'parsing_error': None
                    }
                    f.write(json.dumps(log_entry, default=str) + '\n')
            
            # Define concurrent operations
            async def scan_operation():
                return await history_manager.scan_messages()
            
            async def search_operation():
                return await history_manager.search_messages("integration")
            
            async def check_mail_operation():
                return await history_manager.check_mail("integration-agent-2")
            
            async def status_operation():
                await history_manager.mark_message_read("integration-msg-001")
                await history_manager.add_message_tag("integration-msg-002", "concurrent")
                return True
            
            # Run operations concurrently
            results = await asyncio.gather(
                scan_operation(),
                search_operation(),
                check_mail_operation(),
                status_operation(),
                return_exceptions=True
            )
            
            # Verify all operations completed successfully
            assert len(results) == 4
            assert all(not isinstance(result, Exception) for result in results)
            
            # Verify results
            scan_results, search_results, mail_results, status_result = results
            
            assert len(scan_results) == 5
            assert len(search_results) >= 2
            assert len(mail_results) == 4
            assert status_result is True
            
            # Verify status changes were applied
            status_data = history_manager.message_status.get("integration-msg-001", {})
            assert status_data.get('status') == MessageStatus.READ.value
            
            status_data = history_manager.message_status.get("integration-msg-002", {})
            assert "concurrent" in status_data.get('tags', [])
            
        finally:
            await history_manager.stop()


@pytest.mark.asyncio
class TestMessageHistoryErrorHandling(ReflectiveModule):
    """Test error handling in message history system"""
    
    async def test_corrupted_log_file_handling(self, temp_log_dir):
        """Test handling of corrupted log files"""
        history_manager = MessageHistoryManager(log_directory=temp_log_dir)
        await history_manager.start()
        
        try:
            # Create log file with mixed valid and invalid entries
            log_dir = Path(temp_log_dir)
            log_file = log_dir / "mailbox_corrupted_test.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                # Valid entry
                valid_message = BeastModeMessage(
                    id="valid-msg-001",
                    type=MessageType.SIMPLE_MESSAGE,
                    source="test-agent",
                    payload={"text": "Valid message"}
                )
                valid_entry = {
                    'timestamp': valid_message.timestamp.isoformat(),
                    'channel': 'beast_mode_network',
                    'raw_data': valid_message.model_dump_json(),
                    'parsed_message': valid_message.model_dump(),
                    'parsing_error': None
                }
                f.write(json.dumps(valid_entry, default=str) + '\n')
                
                # Invalid JSON
                f.write('{"invalid": json content}\n')
                
                # Empty line
                f.write('\n')
                
                # Entry with parsing error
                error_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'channel': 'beast_mode_network',
                    'raw_data': '{"malformed": "message"}',
                    'parsed_message': None,
                    'parsing_error': 'Test parsing error'
                }
                f.write(json.dumps(error_entry, default=str) + '\n')
                
                # Another valid entry
                valid_message_2 = BeastModeMessage(
                    id="valid-msg-002",
                    type=MessageType.SYSTEM_HEALTH,
                    source="test-agent-2",
                    payload={"status": "healthy"}
                )
                valid_entry_2 = {
                    'timestamp': valid_message_2.timestamp.isoformat(),
                    'channel': 'beast_mode_network',
                    'raw_data': valid_message_2.model_dump_json(),
                    'parsed_message': valid_message_2.model_dump(),
                    'parsing_error': None
                }
                f.write(json.dumps(valid_entry_2, default=str) + '\n')
            
            # Scan messages - should only get valid entries
            messages = await history_manager.scan_messages()
            
            # Should get 2 valid messages, ignoring corrupted entries
            assert len(messages) == 2
            assert messages[0].message.id in ["valid-msg-001", "valid-msg-002"]
            assert messages[1].message.id in ["valid-msg-001", "valid-msg-002"]
            
        finally:
            await history_manager.stop()
    
    async def test_missing_log_directory(self):
        """Test handling of missing log directory"""
        # Use non-existent directory
        non_existent_dir = "/tmp/non_existent_beast_mode_test"
        
        # Should create directory automatically
        history_manager = MessageHistoryManager(log_directory=non_existent_dir)
        
        assert Path(non_existent_dir).exists()
        
        # Cleanup
        import shutil
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

        shutil.rmtree(non_existent_dir, ignore_errors=True)
    
    async def test_status_file_corruption(self, temp_log_dir):
        """Test handling of corrupted status file"""
        # Create corrupted status file
        log_dir = Path(temp_log_dir)
        status_file = log_dir / "message_status.json"
        
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write('{"corrupted": json content}')
        
        # Should handle corruption gracefully
        history_manager = MessageHistoryManager(log_directory=temp_log_dir)
        
        # Should start with empty status (corruption ignored)
        assert len(history_manager.message_status) == 0
        
        await history_manager.start()

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

        await history_manager.stop()