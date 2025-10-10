"""
Unit tests for security integration with TaskQueueManager
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from src.beast_mode.task_queue.task_queue_manager import TaskQueueManager
from src.beast_mode.task_queue.task_protection import (
    TaskSecurityValidator,
    TaskExecutionSandbox,
    ConversationStateEncryption,
    SecurityThreatLevel,
    SecurityScanResult,
    SandboxExecutionResult,
)
from src.beast_mode.task_queue.models import (
    TaskContext,
    TaskState,
)


class TestSecurityIntegration:
    """Test integration of security components with TaskQueueManager."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create mock Redis client."""
        client = Mock()
        client.ping = AsyncMock(return_value=True)
        client.get = AsyncMock()
        client.set = AsyncMock(return_value=True)
        client.setex = AsyncMock(return_value=True)
        client.delete = AsyncMock(return_value=True)
        client.keys = AsyncMock(return_value=[])
        client.sadd = AsyncMock(return_value=True)
        client.smembers = AsyncMock(return_value=set())
        client.hset = AsyncMock(return_value=True)
        client.hgetall = AsyncMock(return_value={})
        client.zadd = AsyncMock(return_value=True)
        client.zpopmin = AsyncMock(return_value=[])
        client.pipeline = Mock(return_value=AsyncMock())
        return client

    @pytest.fixture
    def task_queue_config(self):
        """Create test TaskQueueConfig with security settings."""
        from types import SimpleNamespace

        # Create configuration objects with required fields using SimpleNamespace
        queue_config = SimpleNamespace()
        queue_config.task_queue_name = "test_task_queue"
        queue_config.max_task_size = 1024 * 1024
        queue_config.max_queue_length = 1000

        persistence_config = SimpleNamespace()
        persistence_config.hot_storage_ttl_hours = 1
        persistence_config.warm_storage_ttl_days = 1
        persistence_config.cold_storage_ttl_days = 30
        persistence_config.checkpoint_storage_ttl_days = 90
        persistence_config.enable_compression = True
        persistence_config.integrity_checking = True

        coordination_config = SimpleNamespace()
        coordination_config.lock_timeout_seconds = 30
        coordination_config.lease_duration_seconds = 60

        security_settings = SimpleNamespace()
        security_settings.dangerous_patterns = ["rm -rf", r"eval\s*\(", r"exec\s*\(", "DROP TABLE"]
        security_settings.max_content_length = 10000

        config = SimpleNamespace()
        config.queue_config = queue_config
        config.persistence_config = persistence_config
        config.coordination_config = coordination_config
        config.security_settings = security_settings
        config.max_consecutive_failures = 5

        return config

    @pytest.fixture
    def test_task_context(self):
        """Create test task context."""
        return TaskContext(
            task_id="test_task_123",
            task_type="data_analysis",
            content={"query": "SELECT * FROM users", "parameters": {"limit": 100}},
            created_at=datetime.now(),
            state=TaskState.PENDING
        )

    @pytest.fixture
    def malicious_task_context(self):
        """Create malicious task context for security testing."""
        return TaskContext(
            task_id="malicious_task_456",
            task_type="system_command",
            content={"command": "rm -rf /", "script": "eval('malicious code')"},
            created_at=datetime.now(),
            state=TaskState.PENDING
        )

    @pytest.fixture
    async def task_queue_manager(self, task_queue_config, mock_redis_client):
        """Create TaskQueueManager with mocked dependencies."""
        with patch('src.beast_mode.task_queue.state_protection.StatePersistenceStrategy.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.state_protection.EnhancedStateIntegrityMonitor.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.state_protection.ConversationStateLockManager.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.state_protection.EnhancedStateIntegrityMonitor.start_continuous_monitoring', new_callable=AsyncMock), \
             patch('src.beast_mode.task_queue.task_protection.TaskDeduplicationManager.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.task_protection.IdempotentTaskProcessor.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.task_protection.PriorityTaskScheduler.__init__', return_value=None):

            manager = TaskQueueManager(task_queue_config, mock_redis_client)

            # Mock all protection components
            manager.state_persistence_strategy = Mock()
            manager.integrity_monitor = Mock()
            manager.state_lock_manager = Mock()
            manager.task_deduplication = Mock()
            manager.idempotent_processor = Mock()
            manager.priority_scheduler = Mock()

            return manager

    @pytest.mark.asyncio
    async def test_security_components_initialization(self, task_queue_config, mock_redis_client):
        """Test that security components are properly initialized."""
        with patch('src.beast_mode.task_queue.state_protection.StatePersistenceStrategy.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.state_protection.EnhancedStateIntegrityMonitor.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.state_protection.ConversationStateLockManager.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.state_protection.EnhancedStateIntegrityMonitor.start_continuous_monitoring', new_callable=AsyncMock), \
             patch('src.beast_mode.task_queue.task_protection.TaskDeduplicationManager.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.task_protection.IdempotentTaskProcessor.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.task_protection.PriorityTaskScheduler.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.task_protection.TaskSecurityValidator.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.task_protection.TaskExecutionSandbox.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.task_protection.ConversationStateEncryption.__init__', return_value=None):

            manager = TaskQueueManager(task_queue_config, mock_redis_client)

            # Verify security components are initialized
            assert hasattr(manager, 'security_validator')
            assert hasattr(manager, 'execution_sandbox')
            assert hasattr(manager, 'state_encryption')

            assert manager.security_validator is not None
            assert manager.execution_sandbox is not None
            assert manager.state_encryption is not None

    @pytest.mark.asyncio
    async def test_validate_task_security_safe_content(self, task_queue_manager, test_task_context):
        """Test security validation with safe content."""
        # Mock security validator to return safe result
        mock_scan_result = SecurityScanResult(
            task_id=test_task_context.task_id,
            threat_level=SecurityThreatLevel.SAFE,
            threats_detected=[],
            safe_to_process=True,
            scan_duration_ms=10.0
        )

        task_queue_manager.security_validator.scan_task_content = AsyncMock(return_value=mock_scan_result)

        result = await task_queue_manager.validate_task_security(test_task_context)

        assert result["success"] is True
        assert result["threat_level"] == "safe"
        assert result["safe_to_process"] is True
        assert result["threats_detected"] == []
        assert result["sanitized_content_available"] is False

    @pytest.mark.asyncio
    async def test_validate_task_security_malicious_content(self, task_queue_manager, malicious_task_context):
        """Test security validation with malicious content."""
        mock_scan_result = SecurityScanResult(
            task_id=malicious_task_context.task_id,
            threat_level=SecurityThreatLevel.HIGH_RISK,
            threats_detected=[
                {
                    "type": "pattern_match",
                    "pattern": "rm -rf",
                    "risk_score": 0.9,
                    "description": "Dangerous file deletion command detected"
                },
                {
                    "type": "pattern_match",
                    "pattern": "eval(",
                    "risk_score": 0.9,
                    "description": "Code evaluation detected"
                }
            ],
            safe_to_process=False,
            scan_duration_ms=25.0
        )

        task_queue_manager.security_validator.scan_task_content = AsyncMock(return_value=mock_scan_result)

        result = await task_queue_manager.validate_task_security(malicious_task_context)

        assert result["success"] is True
        assert result["threat_level"] == "high_risk"
        assert result["safe_to_process"] is False
        assert len(result["threats_detected"]) == 2

    @pytest.mark.asyncio
    async def test_encrypt_decrypt_conversation_state(self, task_queue_manager):
        """Test conversation state encryption and decryption."""
        conversation_data = {
            "conversation_id": "test_conv_123",
            "state": "active",
            "turns": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ],
            "created_at": datetime.now().isoformat()
        }

        # Mock encryption result
        mock_encrypted_result = {
            "encrypted_data": "encrypted_base64_data_here",
            "encryption_timestamp": datetime.now().isoformat(),
            "encryption_version": "1.0",
            "data_integrity_hash": "hash123456",
            "encrypted_size_bytes": 256,
            "original_size_bytes": 180
        }

        task_queue_manager.state_encryption.encrypt_conversation_state = AsyncMock(
            return_value=mock_encrypted_result
        )

        # Test encryption
        encrypt_result = await task_queue_manager.encrypt_conversation_state_secure(conversation_data)

        assert encrypt_result["success"] is True
        assert encrypt_result["encrypted_data"] == "encrypted_base64_data_here"
        assert "encryption_metadata" in encrypt_result

        # Mock decryption
        task_queue_manager.state_encryption.decrypt_conversation_state = AsyncMock(
            return_value=conversation_data
        )

        # Test decryption
        decrypt_result = await task_queue_manager.decrypt_conversation_state_secure(mock_encrypted_result)

        assert decrypt_result["success"] is True
        assert decrypt_result["conversation_data"] == conversation_data
        assert decrypt_result["integrity_verified"] is True

    @pytest.mark.asyncio
    async def test_process_task_with_full_security_safe_task(self, task_queue_manager, test_task_context):
        """Test full security processing with safe task."""
        # Mock security validation - safe
        mock_scan_result = SecurityScanResult(
            task_id=test_task_context.task_id,
            threat_level=SecurityThreatLevel.SAFE,
            threats_detected=[],
            safe_to_process=True,
            scan_duration_ms=10.0
        )

        task_queue_manager.security_validator.scan_task_content = AsyncMock(return_value=mock_scan_result)

        # Mock deduplication
        task_queue_manager.task_deduplication.is_task_already_processed = AsyncMock(return_value=False)

        mock_claim = Mock()
        mock_claim.claim_key = "claim_123"
        task_queue_manager.task_deduplication.claim_task_for_processing = AsyncMock(return_value=mock_claim)

        # Mock sandbox execution - successful
        mock_sandbox_result = SandboxExecutionResult(
            task_id=test_task_context.task_id,
            execution_successful=True,
            result={"status": "completed", "result": "analysis_complete"},
            execution_time_ms=100.0,
            resource_usage={"peak_memory_mb": 50},
            security_violations=[]
        )

        task_queue_manager.execution_sandbox.execute_task_safely = AsyncMock(return_value=mock_sandbox_result)
        task_queue_manager.task_deduplication.complete_task_processing = AsyncMock()

        # Execute secure processing
        result = await task_queue_manager.process_task_with_full_security(test_task_context)

        # Verify successful processing
        assert result["success"] is True
        assert result["task_id"] == test_task_context.task_id
        assert result["claim_id"] == "claim_123"

        security_report = result["security_report"]
        assert security_report["security_scan"]["threat_level"] == "safe"
        assert security_report["security_scan"]["safe_to_process"] is True
        assert security_report["sandbox_execution"]["execution_successful"] is True
        assert security_report["protection_features"]["security_validation"] is True
        assert security_report["protection_features"]["sandboxed_execution"] is True

    @pytest.mark.asyncio
    async def test_process_task_with_full_security_malicious_task_blocked(self, task_queue_manager, malicious_task_context):
        """Test full security processing blocks malicious task."""
        # Mock security validation - malicious
        mock_scan_result = SecurityScanResult(
            task_id=malicious_task_context.task_id,
            threat_level=SecurityThreatLevel.CRITICAL_RISK,
            threats_detected=[
                {
                    "type": "pattern_match",
                    "pattern": "rm -rf",
                    "risk_score": 0.9,
                    "description": "Dangerous file deletion command detected"
                }
            ],
            safe_to_process=False,
            scan_duration_ms=15.0
        )

        task_queue_manager.security_validator.scan_task_content = AsyncMock(return_value=mock_scan_result)

        # Execute secure processing
        result = await task_queue_manager.process_task_with_full_security(malicious_task_context)

        # Verify task was blocked
        assert result["success"] is False
        assert "security validation" in result["error"]
        assert result["task_id"] == malicious_task_context.task_id

        security_report = result["security_report"]
        assert security_report["security_scan"]["threat_level"] == "critical_risk"
        assert security_report["security_scan"]["safe_to_process"] is False
        assert security_report["security_scan"]["threats_detected"] == 1

    @pytest.mark.asyncio
    async def test_process_task_with_full_security_sandbox_violations(self, task_queue_manager, test_task_context):
        """Test full security processing with sandbox violations."""
        # Mock security validation - safe initially
        mock_scan_result = SecurityScanResult(
            task_id=test_task_context.task_id,
            threat_level=SecurityThreatLevel.SAFE,
            threats_detected=[],
            safe_to_process=True,
            scan_duration_ms=10.0
        )

        task_queue_manager.security_validator.scan_task_content = AsyncMock(return_value=mock_scan_result)

        # Mock deduplication
        task_queue_manager.task_deduplication.is_task_already_processed = AsyncMock(return_value=False)

        mock_claim = Mock()
        mock_claim.claim_key = "claim_456"
        task_queue_manager.task_deduplication.claim_task_for_processing = AsyncMock(return_value=mock_claim)

        # Mock sandbox execution - security violations detected
        mock_sandbox_result = SandboxExecutionResult(
            task_id=test_task_context.task_id,
            execution_successful=False,
            error_message="Memory limit exceeded",
            execution_time_ms=200.0,
            resource_usage={"peak_memory_mb": 600},
            security_violations=["Memory limit exceeded: 600MB > 512MB"]
        )

        task_queue_manager.execution_sandbox.execute_task_safely = AsyncMock(return_value=mock_sandbox_result)
        task_queue_manager.task_deduplication.fail_task_processing = AsyncMock()

        # Execute secure processing
        result = await task_queue_manager.process_task_with_full_security(test_task_context)

        # Verify task failed due to sandbox violations
        assert result["success"] is False
        assert "Sandboxed execution failed" in result["error"]
        assert result["claim_id"] == "claim_456"

        security_report = result["security_report"]
        assert security_report["sandbox_execution"]["execution_successful"] is False
        assert security_report["sandbox_execution"]["security_violations"] == 1

    @pytest.mark.asyncio
    async def test_get_security_metrics(self, task_queue_manager):
        """Test aggregated security metrics collection."""
        # Mock individual component metrics
        task_queue_manager.security_validator.get_security_metrics = Mock(return_value={
            "scans_performed": 50,
            "threats_detected": 5,
            "safe_tasks": 45,
            "blocked_tasks": 5
        })

        task_queue_manager.execution_sandbox.get_sandbox_metrics = Mock(return_value={
            "executions_attempted": 45,
            "executions_successful": 40,
            "executions_failed": 5,
            "success_rate": 0.89
        })

        task_queue_manager.state_encryption.get_encryption_metrics = Mock(return_value={
            "encryptions_performed": 100,
            "decryptions_performed": 95,
            "key_rotations": 2,
            "success_rate": 0.98
        })

        metrics = task_queue_manager.get_security_metrics()

        assert "security_components_available" in metrics
        assert metrics["security_components_available"]["security_validator"] is True
        assert metrics["security_components_available"]["execution_sandbox"] is True
        assert metrics["security_components_available"]["state_encryption"] is True

        assert "security_validation" in metrics
        assert metrics["security_validation"]["scans_performed"] == 50
        assert metrics["security_validation"]["threats_detected"] == 5

        assert "sandbox_execution" in metrics
        assert metrics["sandbox_execution"]["success_rate"] == 0.89

        assert "state_encryption" in metrics
        assert metrics["state_encryption"]["success_rate"] == 0.98

    @pytest.mark.asyncio
    async def test_security_component_unavailable_fallback(self, task_queue_config, mock_redis_client):
        """Test graceful fallback when security components are unavailable."""
        with patch('src.beast_mode.task_queue.state_protection.StatePersistenceStrategy.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.state_protection.EnhancedStateIntegrityMonitor.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.state_protection.ConversationStateLockManager.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.state_protection.EnhancedStateIntegrityMonitor.start_continuous_monitoring', new_callable=AsyncMock), \
             patch('src.beast_mode.task_queue.task_protection.TaskDeduplicationManager.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.task_protection.IdempotentTaskProcessor.__init__', return_value=None), \
             patch('src.beast_mode.task_queue.task_protection.PriorityTaskScheduler.__init__', return_value=None):

            manager = TaskQueueManager(task_queue_config, mock_redis_client)

            # Simulate missing security components
            manager.security_validator = None
            manager.execution_sandbox = None
            manager.state_encryption = None

            test_task = TaskContext(
                task_id="test_task_fallback",
                task_type="simple_task",
                content={"data": "test"},
                created_at=datetime.now(),
                state=TaskState.PENDING
            )

            # Test security validation fallback
            result = await manager.validate_task_security(test_task)
            assert result["success"] is False
            assert "Security validator not available" in result["error"]

            # Test encryption fallback
            conversation_data = {"test": "data"}
            result = await manager.encrypt_conversation_state_secure(conversation_data)
            assert result["success"] is False
            assert "State encryption not available" in result["error"]

            # Test decryption fallback
            result = await manager.decrypt_conversation_state_secure({"encrypted_data": "test"})
            assert result["success"] is False
            assert "State encryption not available" in result["error"]

    @pytest.mark.asyncio
    async def test_low_risk_task_with_sanitization(self, task_queue_manager):
        """Test processing of low-risk task with content sanitization."""
        low_risk_task = TaskContext(
            task_id="low_risk_task",
            task_type="script_processing",
            content={"script": "<script>alert('test')</script>console.log('safe');"},
            created_at=datetime.now(),
            state=TaskState.PENDING
        )

        # Mock security validation - low risk with sanitized content
        mock_scan_result = SecurityScanResult(
            task_id=low_risk_task.task_id,
            threat_level=SecurityThreatLevel.LOW_RISK,
            threats_detected=[
                {
                    "type": "pattern_match",
                    "pattern": "<script",
                    "risk_score": 0.3,
                    "description": "Script tag detected"
                }
            ],
            safe_to_process=True,
            sanitized_content={"script": "&lt;script&gt;alert('test')&lt;/script&gt;console.log('safe');"},
            scan_duration_ms=20.0
        )

        task_queue_manager.security_validator.scan_task_content = AsyncMock(return_value=mock_scan_result)

        # Mock deduplication and sandbox as successful
        task_queue_manager.task_deduplication.is_task_already_processed = AsyncMock(return_value=False)

        mock_claim = Mock()
        mock_claim.claim_key = "claim_sanitized"
        task_queue_manager.task_deduplication.claim_task_for_processing = AsyncMock(return_value=mock_claim)

        mock_sandbox_result = SandboxExecutionResult(
            task_id=low_risk_task.task_id,
            execution_successful=True,
            result={"status": "completed", "sanitized": True},
            execution_time_ms=80.0,
            resource_usage={"peak_memory_mb": 30},
            security_violations=[]
        )

        task_queue_manager.execution_sandbox.execute_task_safely = AsyncMock(return_value=mock_sandbox_result)
        task_queue_manager.task_deduplication.complete_task_processing = AsyncMock()

        # Execute secure processing
        result = await task_queue_manager.process_task_with_full_security(low_risk_task)

        # Verify successful processing with sanitization
        assert result["success"] is True

        security_report = result["security_report"]
        assert security_report["security_scan"]["threat_level"] == "low_risk"
        assert security_report["security_scan"]["safe_to_process"] is True
        assert security_report["security_scan"]["threats_detected"] == 1
        assert security_report["sandbox_execution"]["execution_successful"] is True

        # Verify sanitized content was used (task content should be modified)
        assert low_risk_task.content == {"script": "&lt;script&gt;alert('test')&lt;/script&gt;console.log('safe');"}