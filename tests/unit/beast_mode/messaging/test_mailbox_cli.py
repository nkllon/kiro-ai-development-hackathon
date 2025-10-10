#!/usr/bin/env python3
"""Tests for Beast Mailbox Service one-shot inspector CLI."""

import asyncio
import json
import logging
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Import the modules we're testing
from src.beast_mode.messaging.redis_mailbox import (
    MailboxMessage,
    RedisMailboxService,
)
from src.beast_mode.messaging.redis_foundation import RedisConfig


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client for testing."""
    client = AsyncMock()
    client.xrevrange = AsyncMock(return_value=[])
    client.xack = AsyncMock(return_value=0)
    client.xdel = AsyncMock(return_value=0)
    client.xgroup_create = AsyncMock()
    return client


@pytest.fixture
def mock_redis_foundation(mock_redis_client):
    """Create a mock RedisFoundation for testing."""
    foundation = AsyncMock()
    foundation.initialize = AsyncMock(return_value=True)
    foundation.shutdown = AsyncMock()
    foundation.client = mock_redis_client
    return foundation


@pytest.fixture
def mailbox_service(mock_redis_foundation):
    """Create a minimal service mock for testing."""
    service = MagicMock()
    service.agent_id = "test-agent"
    service.inbox_stream = "beast:mailbox:test-agent:in"
    service.redis = mock_redis_foundation
    return service


@pytest.fixture
def sample_messages() -> List[tuple[bytes, Dict[bytes, bytes]]]:
    """Create sample Redis stream entries for testing."""
    return [
        (
            b"1234567890-0",
            {
                b"message_id": b"msg-001",
                b"sender": b"alice",
                b"recipient": b"test-agent",
                b"payload": b'{"text": "Hello World"}',
                b"message_type": b"direct_message",
                b"timestamp": b"1234567890.0",
            },
        ),
        (
            b"1234567891-0",
            {
                b"message_id": b"msg-002",
                b"sender": b"bob",
                b"recipient": b"test-agent",
                b"payload": b'{"text": "Test message"}',
                b"message_type": b"direct_message",
                b"timestamp": b"1234567891.0",
            },
        ),
    ]


class TestMailboxMessageDecoding:
    """Test MailboxMessage payload decoding with various field types."""

    def test_from_redis_fields_with_bytes(self):
        """Test decoding Redis fields when all values are bytes."""
        fields = {
            b"message_id": b"msg-001",
            b"sender": b"alice",
            b"recipient": b"bob",
            b"payload": b'{"text": "Hello"}',
            b"message_type": b"direct_message",
            b"timestamp": b"1234567890.0",
        }
        
        message = MailboxMessage.from_redis_fields(fields)
        
        assert message.message_id == "msg-001"
        assert message.sender == "alice"
        assert message.recipient == "bob"
        assert message.payload == {"text": "Hello"}
        assert message.message_type == "direct_message"
        assert message.timestamp == 1234567890.0

    def test_from_redis_fields_with_strings(self):
        """Test decoding Redis fields when values are strings."""
        fields = {
            "message_id": "msg-002",
            "sender": "charlie",
            "recipient": "dave",
            "payload": '{"count": 42}',
            "message_type": "notification",
            "timestamp": "9876543210.5",
        }
        
        message = MailboxMessage.from_redis_fields(fields)
        
        assert message.message_id == "msg-002"
        assert message.sender == "charlie"
        assert message.recipient == "dave"
        assert message.payload == {"count": 42}
        assert message.message_type == "notification"
        assert message.timestamp == 9876543210.5

    def test_from_redis_fields_with_mixed_types(self):
        """Test decoding Redis fields with mixed byte/string types."""
        fields = {
            b"message_id": "msg-003",
            "sender": b"eve",
            b"recipient": "frank",
            "payload": b'{"status": "ok"}',
            b"message_type": "status_update",
            "timestamp": b"1111111111.0",
        }
        
        message = MailboxMessage.from_redis_fields(fields)
        
        assert message.message_id == "msg-003"
        assert message.sender == "eve"
        assert message.recipient == "frank"
        assert message.payload == {"status": "ok"}
        assert message.message_type == "status_update"


class TestLatestReadOnlyMode:
    """Test --latest read-only mode without destructive operations."""

    @pytest.mark.asyncio
    async def test_fetch_latest_no_messages(self, mailbox_service, mock_redis_client):
        """Test fetching latest messages when stream is empty."""
        mock_redis_client.xrevrange.return_value = []
        
        # Import the function we're testing
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        # Should not raise an exception, just log and return
        await _fetch_latest_messages(mailbox_service, count=1, ack=False, trim=False)
        
        # Verify Redis was queried
        mock_redis_client.xrevrange.assert_called_once()
        # Verify no ack/delete operations were attempted
        mock_redis_client.xack.assert_not_called()
        mock_redis_client.xdel.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_latest_single_message(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test fetching a single latest message."""
        mock_redis_client.xrevrange.return_value = sample_messages[:1]
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        await _fetch_latest_messages(mailbox_service, count=1, ack=False, trim=False)
        
        # Verify correct stream was queried
        call_args = mock_redis_client.xrevrange.call_args
        assert call_args[0][0] == "beast:mailbox:test-agent:in"
        assert call_args[1]["count"] == 1
        
        # Verify no destructive operations
        mock_redis_client.xack.assert_not_called()
        mock_redis_client.xdel.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_latest_multiple_messages(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test fetching multiple latest messages."""
        mock_redis_client.xrevrange.return_value = sample_messages
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        await _fetch_latest_messages(mailbox_service, count=2, ack=False, trim=False)
        
        # Verify correct count was requested
        call_args = mock_redis_client.xrevrange.call_args
        assert call_args[1]["count"] == 2
        
        # Verify no destructive operations
        mock_redis_client.xack.assert_not_called()
        mock_redis_client.xdel.assert_not_called()


class TestAcknowledgeBehavior:
    """Test --ack flag behavior for acknowledging messages."""

    @pytest.mark.asyncio
    async def test_ack_single_message(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test acknowledging a single message."""
        mock_redis_client.xrevrange.return_value = sample_messages[:1]
        mock_redis_client.xack.return_value = 1
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        await _fetch_latest_messages(mailbox_service, count=1, ack=True, trim=False)
        
        # Verify consumer group was created
        mock_redis_client.xgroup_create.assert_called_once()
        
        # Verify acknowledgement was performed
        mock_redis_client.xack.assert_called_once()
        call_args = mock_redis_client.xack.call_args
        assert call_args[0][0] == "beast:mailbox:test-agent:in"
        assert call_args[0][1] == "test-agent:group"
        assert b"1234567890-0" in call_args[0]
        
        # Verify no delete operation
        mock_redis_client.xdel.assert_not_called()

    @pytest.mark.asyncio
    async def test_ack_multiple_messages(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test acknowledging multiple messages."""
        mock_redis_client.xrevrange.return_value = sample_messages
        mock_redis_client.xack.return_value = 2
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        await _fetch_latest_messages(mailbox_service, count=2, ack=True, trim=False)
        
        # Verify all message IDs were acknowledged
        call_args = mock_redis_client.xack.call_args
        assert b"1234567890-0" in call_args[0]
        assert b"1234567891-0" in call_args[0]
        
        # Verify no delete operation
        mock_redis_client.xdel.assert_not_called()

    @pytest.mark.asyncio
    async def test_ack_with_existing_consumer_group(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test acknowledgement when consumer group already exists."""
        mock_redis_client.xrevrange.return_value = sample_messages[:1]
        mock_redis_client.xack.return_value = 1
        # Simulate BUSYGROUP error
        mock_redis_client.xgroup_create.side_effect = Exception("BUSYGROUP Consumer Group name already exists")
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        # Should handle the error gracefully
        await _fetch_latest_messages(mailbox_service, count=1, ack=True, trim=False)
        
        # Verify acknowledgement still happened
        mock_redis_client.xack.assert_called_once()

    @pytest.mark.asyncio
    async def test_ack_failure_raises_error(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test that acknowledgement failures are properly reported."""
        mock_redis_client.xrevrange.return_value = sample_messages[:1]
        mock_redis_client.xack.side_effect = Exception("Redis connection lost")
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        # Should raise SystemExit on ack failure
        with pytest.raises(SystemExit) as exc_info:
            await _fetch_latest_messages(mailbox_service, count=1, ack=True, trim=False)
        
        assert "Acknowledgement failed" in str(exc_info.value)


class TestTrimBehavior:
    """Test --trim flag behavior for deleting messages."""

    @pytest.mark.asyncio
    async def test_trim_single_message(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test deleting a single message."""
        mock_redis_client.xrevrange.return_value = sample_messages[:1]
        mock_redis_client.xack.return_value = 1
        mock_redis_client.xdel.return_value = 1
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        await _fetch_latest_messages(mailbox_service, count=1, ack=True, trim=True)
        
        # Verify acknowledgement happened first
        mock_redis_client.xack.assert_called_once()
        
        # Verify deletion was performed
        mock_redis_client.xdel.assert_called_once()
        call_args = mock_redis_client.xdel.call_args
        assert call_args[0][0] == "beast:mailbox:test-agent:in"
        assert b"1234567890-0" in call_args[0]

    @pytest.mark.asyncio
    async def test_trim_multiple_messages(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test deleting multiple messages."""
        mock_redis_client.xrevrange.return_value = sample_messages
        mock_redis_client.xack.return_value = 2
        mock_redis_client.xdel.return_value = 2
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        await _fetch_latest_messages(mailbox_service, count=2, ack=True, trim=True)
        
        # Verify all message IDs were deleted
        call_args = mock_redis_client.xdel.call_args
        assert b"1234567890-0" in call_args[0]
        assert b"1234567891-0" in call_args[0]

    @pytest.mark.asyncio
    async def test_trim_without_ack(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test that trim works even if ack is False."""
        mock_redis_client.xrevrange.return_value = sample_messages[:1]
        mock_redis_client.xdel.return_value = 1
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        await _fetch_latest_messages(mailbox_service, count=1, ack=False, trim=True)
        
        # Verify no acknowledgement
        mock_redis_client.xack.assert_not_called()
        
        # Verify deletion still happened
        mock_redis_client.xdel.assert_called_once()

    @pytest.mark.asyncio
    async def test_trim_failure_raises_error(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test that deletion failures are properly reported."""
        mock_redis_client.xrevrange.return_value = sample_messages[:1]
        mock_redis_client.xdel.side_effect = Exception("Redis write error")
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        # Should raise SystemExit on delete failure
        with pytest.raises(SystemExit) as exc_info:
            await _fetch_latest_messages(mailbox_service, count=1, ack=False, trim=True)
        
        assert "Deletion failed" in str(exc_info.value)


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_redis_initialization_failure(self, mailbox_service):
        """Test handling of Redis connection failure."""
        mailbox_service.redis.initialize = AsyncMock(return_value=False)
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        # Should raise SystemExit when Redis fails to initialize
        with pytest.raises(SystemExit) as exc_info:
            await _fetch_latest_messages(mailbox_service, count=1, ack=False, trim=False)
        
        assert "Failed to connect to Redis" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_redis_client_unavailable(self, mailbox_service):
        """Test handling when Redis client is None after initialization."""
        mailbox_service.redis.initialize = AsyncMock(return_value=True)
        mailbox_service.redis.client = None
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        # Should raise SystemExit when client is unavailable
        with pytest.raises(SystemExit) as exc_info:
            await _fetch_latest_messages(mailbox_service, count=1, ack=False, trim=False)
        
        assert "Redis client unavailable" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_consumer_group_creation_failure(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test handling of consumer group creation failure (non-BUSYGROUP)."""
        mock_redis_client.xrevrange.return_value = sample_messages[:1]
        mock_redis_client.xgroup_create.side_effect = Exception("Permission denied")
        mock_redis_client.xack.return_value = 1
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        # Should still attempt to acknowledge even if group creation fails
        await _fetch_latest_messages(mailbox_service, count=1, ack=True, trim=False)
        
        # Verify acknowledgement was attempted
        mock_redis_client.xack.assert_called_once()

    @pytest.mark.asyncio
    async def test_partial_ack_failure(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test handling when not all messages are acknowledged."""
        mock_redis_client.xrevrange.return_value = sample_messages
        # Only 1 message acknowledged out of 2
        mock_redis_client.xack.return_value = 1
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        # Should complete without error (Redis reports what was actually acked)
        await _fetch_latest_messages(mailbox_service, count=2, ack=True, trim=False)
        
        mock_redis_client.xack.assert_called_once()

    @pytest.mark.asyncio
    async def test_partial_delete_failure(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test handling when not all messages are deleted."""
        mock_redis_client.xrevrange.return_value = sample_messages
        # Only 1 message deleted out of 2
        mock_redis_client.xdel.return_value = 1
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        # Should complete without error (Redis reports what was actually deleted)
        await _fetch_latest_messages(mailbox_service, count=2, ack=False, trim=True)
        
        mock_redis_client.xdel.assert_called_once()


class TestShutdownBehavior:
    """Test that Redis shutdown is always called."""

    @pytest.mark.asyncio
    async def test_shutdown_on_success(
        self, mailbox_service, mock_redis_client, sample_messages
    ):
        """Test that Redis is properly shut down after successful operation."""
        mock_redis_client.xrevrange.return_value = sample_messages[:1]
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        await _fetch_latest_messages(mailbox_service, count=1, ack=False, trim=False)
        
        # Verify shutdown was called
        mailbox_service.redis.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_on_error(self, mailbox_service, mock_redis_client):
        """Test that Redis is properly shut down even on error."""
        mock_redis_client.xrevrange.side_effect = Exception("Unexpected error")
        
        from scripts.run_mailbox_service import _fetch_latest_messages
        
        # Should raise the exception but still shut down
        with pytest.raises(Exception):
            await _fetch_latest_messages(mailbox_service, count=1, ack=False, trim=False)
        
        # Verify shutdown was called despite error
        mailbox_service.redis.shutdown.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

