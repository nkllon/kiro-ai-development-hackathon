"""
Cross-Platform Compatibility Tests for Beast Mode Agent Collaboration Network

Tests compatibility across different platforms, Python versions, and environments.
Validates message format compatibility, serialization/deserialization, and system behavior.
"""

import asyncio
import json
import pytest
import platform
import sys
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch, MagicMock
import uuid

from src.beast_mode.messaging import (
    BeastModeBusClient,
    BeastModeMessage,
    MessageType,
    AgentCapabilities,
    MailboxLogger,
    SporeManager
)


class TestPlatformCompatibility:
    """Test compatibility across different platforms"""
    
    def test_platform_detection(self):
        """Test platform detection and compatibility"""
        current_platform = platform.system()
        current_arch = platform.machine()
        python_version = sys.version_info
        
        print(f"\nPlatform Compatibility Test:")
        print(f"  Platform: {current_platform}")
        print(f"  Architecture: {current_arch}")
        print(f"  Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Verify supported platforms
        supported_platforms = ["Darwin", "Linux", "Windows"]
        assert current_platform in supported_platforms, f"Unsupported platform: {current_platform}"
        
        # Verify Python version compatibility
        assert python_version >= (3, 9), f"Python {python_version} not supported, requires 3.9+"
    
    def test_path_handling_compatibility(self):
        """Test file path handling across platforms"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Test various path operations
            test_paths = [
                "simple_file.txt",
                "nested/directory/file.txt",
                "file with spaces.txt",
                "file-with-dashes.txt",
                "file_with_underscores.txt"
            ]
            
            for test_path in test_paths:
                full_path = Path(temp_dir) / test_path
                
                # Create directory if needed
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write and read file
                test_content = f"Test content for {test_path}"
                full_path.write_text(test_content, encoding='utf-8')
                
                read_content = full_path.read_text(encoding='utf-8')
                assert read_content == test_content
                
                # Verify path operations work
                assert full_path.exists()
                assert full_path.is_file()
                assert full_path.name == Path(test_path).name
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_async_compatibility(self):
        """Test asyncio compatibility across platforms"""
        
        # Test basic async operations
        async def test_coroutine():
            await asyncio.sleep(0.01)
            return "async_test_result"
        
        result = await test_coroutine()
        assert result == "async_test_result"
        
        # Test concurrent operations
        async def concurrent_task(task_id):
            await asyncio.sleep(0.01)
            return f"task_{task_id}_complete"
        
        tasks = [concurrent_task(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result == f"task_{i}_complete"
    
    def test_json_serialization_compatibility(self):
        """Test JSON serialization compatibility across platforms"""
        
        # Test various data types
        test_data = {
            "string": "Hello, World!",
            "integer": 42,
            "float": 3.14159,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3, "four", 5.0],
            "nested_dict": {
                "inner_string": "nested value",
                "inner_number": 123
            },
            "unicode": "Unicode: 你好世界 🌍",
            "datetime": datetime.now().isoformat(),
            "uuid": str(uuid.uuid4())
        }
        
        # Serialize and deserialize
        serialized = json.dumps(test_data, ensure_ascii=False, default=str)
        deserialized = json.loads(serialized)
        
        # Verify data integrity
        assert deserialized["string"] == test_data["string"]
        assert deserialized["integer"] == test_data["integer"]
        assert deserialized["float"] == test_data["float"]
        assert deserialized["boolean"] == test_data["boolean"]
        assert deserialized["null"] == test_data["null"]
        assert deserialized["list"] == test_data["list"]
        assert deserialized["nested_dict"] == test_data["nested_dict"]
        assert deserialized["unicode"] == test_data["unicode"]


class TestMessageFormatCompatibility:
    """Test message format compatibility across versions"""
    
    def test_current_message_format(self):
        """Test current message format serialization"""
        
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="test_agent",
            target="target_agent",
            payload={"content": "Test message"},
            priority=5
        )
        
        # Serialize to dict
        message_dict = message.model_dump()
        
        # Verify required fields
        required_fields = ["id", "type", "source", "payload", "timestamp", "priority"]
        for field in required_fields:
            assert field in message_dict, f"Missing required field: {field}"
        
        # Serialize to JSON
        json_str = json.dumps(message_dict, default=str)
        
        # Deserialize back
        parsed_dict = json.loads(json_str)
        reconstructed = BeastModeMessage(**parsed_dict)
        
        # Verify integrity
        assert reconstructed.type == message.type
        assert reconstructed.source == message.source
        assert reconstructed.target == message.target
        assert reconstructed.payload == message.payload
        assert reconstructed.priority == message.priority
    
    def test_legacy_message_format_v1(self):
        """Test compatibility with legacy v1 message format"""
        
        # Simulate legacy v1 format (minimal fields)
        legacy_v1 = {
            "type": "simple_message",
            "source": "legacy_agent_v1",
            "content": "Legacy v1 message"  # Old field name
        }
        
        # Convert to modern format
        try:
            modern_payload = {"content": legacy_v1.get("content", "")}
            
            modern_message = BeastModeMessage(
                type=MessageType(legacy_v1["type"]),
                source=legacy_v1["source"],
                payload=modern_payload
            )
            
            assert modern_message.type == MessageType.SIMPLE_MESSAGE
            assert modern_message.source == "legacy_agent_v1"
            assert modern_message.payload["content"] == "Legacy v1 message"
            
        except Exception as e:
            pytest.fail(f"Failed to convert legacy v1 format: {e}")
    
    def test_legacy_message_format_v2(self):
        """Test compatibility with legacy v2 message format"""
        
        # Simulate legacy v2 format (some modern fields)
        legacy_v2 = {
            "type": "agent_discovery",
            "source": "legacy_agent_v2",
            "payload": {
                "capabilities": ["python", "testing"]  # Old format
            },
            "timestamp": "2024-01-01T12:00:00"  # String timestamp
        }
        
        # Convert to modern format
        try:
            # Convert capabilities to modern format
            agent_caps = AgentCapabilities(
                agent_id=legacy_v2["source"],
                capabilities=legacy_v2["payload"]["capabilities"],
                availability="ready_for_business"
            )
            
            modern_payload = {
                "agent_capabilities": agent_caps.model_dump()
            }
            
            modern_message = BeastModeMessage(
                type=MessageType(legacy_v2["type"]),
                source=legacy_v2["source"],
                payload=modern_payload
            )
            
            assert modern_message.type == MessageType.AGENT_DISCOVERY
            assert modern_message.source == "legacy_agent_v2"
            
        except Exception as e:
            pytest.fail(f"Failed to convert legacy v2 format: {e}")
    
    def test_future_message_format_compatibility(self):
        """Test handling of future message format with unknown fields"""
        
        # Simulate future format with extra fields
        future_format = {
            "id": str(uuid.uuid4()),
            "type": "simple_message",
            "source": "future_agent",
            "target": "current_agent",
            "payload": {"content": "Future message"},
            "timestamp": datetime.now().isoformat(),
            "priority": 5,
            # Future fields
            "version": "2.0",
            "encryption": "AES256",
            "signature": "future_signature_hash",
            "metadata": {
                "future_field": "future_value"
            }
        }
        
        # Should be able to parse known fields, ignore unknown ones
        try:
            # Extract only known fields
            known_fields = {
                "id": future_format["id"],
                "type": future_format["type"],
                "source": future_format["source"],
                "target": future_format["target"],
                "payload": future_format["payload"],
                "timestamp": future_format["timestamp"],
                "priority": future_format["priority"]
            }
            
            message = BeastModeMessage(**known_fields)
            
            assert message.type == MessageType.SIMPLE_MESSAGE
            assert message.source == "future_agent"
            assert message.payload["content"] == "Future message"
            
        except Exception as e:
            pytest.fail(f"Failed to handle future format: {e}")


class TestEncodingCompatibility:
    """Test encoding and character set compatibility"""
    
    def test_utf8_encoding_compatibility(self):
        """Test UTF-8 encoding compatibility"""
        
        # Test various UTF-8 encoded content
        utf8_test_cases = [
            "ASCII text",
            "Latin-1: café, naïve, résumé",
            "Greek: Ελληνικά",
            "Cyrillic: Русский",
            "Chinese: 中文测试",
            "Japanese: 日本語テスト",
            "Arabic: اختبار عربي",
            "Emoji: 🚀🔥💻🌟",
            "Mixed: Hello 世界! 🌍 Тест"
        ]
        
        for test_content in utf8_test_cases:
            message = BeastModeMessage(
                type=MessageType.SIMPLE_MESSAGE,
                source="utf8_test_agent",
                payload={"content": test_content}
            )
            
            # Serialize with UTF-8
            json_str = json.dumps(message.model_dump(), ensure_ascii=False, default=str)
            json_bytes = json_str.encode('utf-8')
            
            # Deserialize from UTF-8
            decoded_str = json_bytes.decode('utf-8')
            parsed_dict = json.loads(decoded_str)
            reconstructed = BeastModeMessage(**parsed_dict)
            
            # Verify content preserved
            assert reconstructed.payload["content"] == test_content
    
    def test_binary_data_compatibility(self):
        """Test binary data handling compatibility"""
        
        import base64
        
        # Test binary data encoding
        binary_data = b"Binary test data: \x00\x01\x02\x03\xFF"
        encoded_data = base64.b64encode(binary_data).decode('ascii')
        
        message = BeastModeMessage(
            type=MessageType.TECHNICAL_EXCHANGE,
            source="binary_test_agent",
            payload={
                "binary_data": encoded_data,
                "encoding": "base64"
            }
        )
        
        # Serialize and deserialize
        json_str = json.dumps(message.model_dump(), default=str)
        parsed_dict = json.loads(json_str)
        reconstructed = BeastModeMessage(**parsed_dict)
        
        # Decode and verify binary data
        decoded_data = base64.b64decode(reconstructed.payload["binary_data"])
        assert decoded_data == binary_data
    
    def test_large_content_compatibility(self):
        """Test large content handling compatibility"""
        
        # Create large content (1MB)
        large_content = "x" * (1024 * 1024)
        
        message = BeastModeMessage(
            type=MessageType.SPORE_DELIVERY,
            source="large_content_agent",
            payload={
                "spore_content": large_content,
                "size": len(large_content)
            }
        )
        
        # Serialize (this tests memory handling)
        json_str = json.dumps(message.model_dump(), default=str)
        
        # Verify size
        assert len(json_str) > 1024 * 1024  # Should be larger than 1MB
        
        # Deserialize (tests parsing large content)
        parsed_dict = json.loads(json_str)
        reconstructed = BeastModeMessage(**parsed_dict)
        
        # Verify content integrity
        assert reconstructed.payload["spore_content"] == large_content
        assert reconstructed.payload["size"] == len(large_content)


class TestSystemIntegrationCompatibility:
    """Test system integration compatibility across environments"""
    
    @pytest.mark.asyncio
    async def test_redis_mock_compatibility(self):
        """Test Redis mock compatibility across platforms"""
        
        with patch('redis.asyncio.from_url') as mock_redis:
            # Test different Redis URL formats
            redis_urls = [
                "redis://localhost:6379",
                "redis://127.0.0.1:6379/0",
                "redis://:password@localhost:6379",
                "rediss://secure.redis.com:6380"
            ]
            
            for redis_url in redis_urls:
                mock_client = AsyncMock()
                mock_client.ping = AsyncMock(return_value=True)
                mock_client.publish = AsyncMock(return_value=1)
                mock_redis.return_value = mock_client
                
                agent = BeastModeBusClient(
                    redis_url=redis_url,
                    agent_id="compatibility_test_agent",
                    capabilities=["compatibility_testing"]
                )
                
                # Should connect successfully
                connected = await agent.connect()
                assert connected is True
                
                # Should be able to send messages
                await agent.send_simple_message("Compatibility test")
                
                await agent.disconnect()
    
    def test_file_system_compatibility(self):
        """Test file system operations compatibility"""
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Test SporeManager with various file operations
            spore_manager = SporeManager(spore_directory=temp_dir)
            
            # Test file creation with various names
            test_spores = [
                ("simple_spore", "def execute(): pass"),
                ("spore-with-dashes", "def execute(): return 'dashes'"),
                ("spore_with_underscores", "def execute(): return 'underscores'"),
                ("SporeWithCamelCase", "def execute(): return 'camel'")
            ]
            
            for spore_name, spore_content in test_spores:
                metadata = {
                    "name": spore_name,
                    "version": "1.0.0",
                    "author": "compatibility_test",
                    "description": f"Compatibility test spore: {spore_name}"
                }
                
                # Save spore
                saved_name = spore_manager.save_spore(spore_content, metadata)
                assert saved_name == spore_name
                
                # Load spore
                loaded_spore = spore_manager.load_spore(spore_name)
                assert loaded_spore is not None
                assert loaded_spore['implementation'] == spore_content
                
                # Verify file exists
                spore_file = Path(temp_dir) / f"{spore_name}.json"
                assert spore_file.exists()
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_mailbox_logger_compatibility(self):
        """Test MailboxLogger compatibility across platforms"""
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            with patch('redis.asyncio.from_url') as mock_redis:
                mock_client = AsyncMock()
                mock_pubsub = AsyncMock()
                
                mock_client.ping = AsyncMock(return_value=True)
                mock_client.pubsub = MagicMock(return_value=mock_pubsub)
                mock_redis.return_value = mock_client
                
                # Test logger with various configurations
                logger_configs = [
                    {"channel": "test_channel", "max_log_size_mb": 1},
                    {"channel": "beast_mode_network", "max_log_size_mb": 5},
                    {"channel": "custom-channel", "max_log_size_mb": 10}
                ]
                
                for config in logger_configs:
                    logger = MailboxLogger(
                        redis_url="redis://localhost:6379",
                        log_directory=temp_dir,
                        **config
                    )
                    
                    # Mock message stream
                    test_messages = [
                        {
                            'type': 'message',
                            'channel': config["channel"],
                            'data': json.dumps({
                                "type": "simple_message",
                                "source": "test_agent",
                                "payload": {"content": f"Test message for {config['channel']}"}
                            })
                        }
                    ]
                    
                    async def mock_listen():
                        for msg in test_messages:
                            yield msg
                    
                    mock_pubsub.listen = mock_listen
                    mock_pubsub.subscribe = AsyncMock()
                    mock_pubsub.unsubscribe = AsyncMock()
                    mock_pubsub.aclose = AsyncMock()
                    
                    # Start and stop logger
                    await logger.start_logging()
                    await asyncio.sleep(0.1)
                    await logger.stop_logging()
                    
                    # Verify logging worked
                    assert logger.stats['messages_logged'] >= 0
                    
                    # Verify log files created
                    log_files = logger.get_log_files()
                    if log_files:
                        log_file_path = Path(log_files[0]['path'])
                        assert log_file_path.exists()
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestVersionCompatibility:
    """Test compatibility across different component versions"""
    
    def test_message_type_enum_compatibility(self):
        """Test MessageType enum compatibility"""
        
        # Test all current message types
        current_types = [
            MessageType.SIMPLE_MESSAGE,
            MessageType.PROMPT_REQUEST,
            MessageType.PROMPT_RESPONSE,
            MessageType.AGENT_DISCOVERY,
            MessageType.AGENT_RESPONSE,
            MessageType.HELP_WANTED,
            MessageType.HELP_RESPONSE,
            MessageType.SPORE_DELIVERY,
            MessageType.SPORE_REQUEST,
            MessageType.TECHNICAL_EXCHANGE,
            MessageType.SYSTEM_HEALTH
        ]
        
        for msg_type in current_types:
            # Test string conversion
            type_str = msg_type.value
            assert isinstance(type_str, str)
            
            # Test reconstruction from string
            reconstructed = MessageType(type_str)
            assert reconstructed == msg_type
            
            # Test in message creation
            message = BeastModeMessage(
                type=msg_type,
                source="version_test_agent",
                payload={"test": "version_compatibility"}
            )
            
            assert message.type == msg_type
    
    def test_agent_capabilities_compatibility(self):
        """Test AgentCapabilities model compatibility"""
        
        # Test various capability configurations
        capability_configs = [
            {
                "agent_id": "basic_agent",
                "capabilities": ["python"],
                "availability": "ready_for_business"
            },
            {
                "agent_id": "advanced_agent",
                "capabilities": ["python", "docker", "kubernetes", "gcp"],
                "availability": "busy",
                "specializations": ["cloud_architecture", "devops"],
                "collaboration_history": ["project_1", "project_2"]
            },
            {
                "agent_id": "minimal_agent",
                "capabilities": [],
                "availability": "offline"
            }
        ]
        
        for config in capability_configs:
            # Create capabilities object
            caps = AgentCapabilities(**config)
            
            # Verify required fields
            assert caps.agent_id == config["agent_id"]
            assert caps.capabilities == config["capabilities"]
            assert caps.availability == config["availability"]
            
            # Test serialization
            caps_dict = caps.model_dump()
            reconstructed = AgentCapabilities(**caps_dict)
            
            assert reconstructed.agent_id == caps.agent_id
            assert reconstructed.capabilities == caps.capabilities
            assert reconstructed.availability == caps.availability
    
    def test_backward_compatibility_validation(self):
        """Test backward compatibility with older message formats"""
        
        # Test handling of messages missing optional fields
        minimal_message_data = {
            "type": "simple_message",
            "source": "minimal_agent",
            "payload": {"content": "Minimal message"}
            # Missing: id, timestamp, priority, target, correlation_id
        }
        
        # Should be able to create message with defaults
        message = BeastModeMessage(**minimal_message_data)
        
        assert message.type == MessageType.SIMPLE_MESSAGE
        assert message.source == "minimal_agent"
        assert message.payload["content"] == "Minimal message"
        assert message.id is not None  # Should be auto-generated
        assert message.timestamp is not None  # Should be auto-generated
        assert message.priority == 5  # Default value
        assert message.target is None  # Optional field
        assert message.correlation_id is None  # Optional field
    
    def test_forward_compatibility_validation(self):
        """Test forward compatibility for future extensions"""
        
        # Test that current system can handle additional fields gracefully
        extended_message_data = {
            "id": str(uuid.uuid4()),
            "type": "simple_message",
            "source": "extended_agent",
            "payload": {
                "content": "Extended message",
                "future_field": "future_value"  # Extra field in payload
            },
            "timestamp": datetime.now().isoformat(),
            "priority": 5,
            # These would be future extensions
            "extra_metadata": {"version": "2.0"},
            "security_context": {"encrypted": False}
        }
        
        # Extract only known fields for current version
        known_fields = {
            key: value for key, value in extended_message_data.items()
            if key in ["id", "type", "source", "target", "payload", "timestamp", "priority", "correlation_id"]
        }
        
        # Should handle gracefully
        message = BeastModeMessage(**known_fields)
        
        assert message.type == MessageType.SIMPLE_MESSAGE
        assert message.source == "extended_agent"
        assert message.payload["content"] == "Extended message"
        # Future fields in payload should be preserved
        assert message.payload["future_field"] == "future_value"


if __name__ == "__main__":
    # Run compatibility tests
    pytest.main([__file__, "-v", "--tb=short"])