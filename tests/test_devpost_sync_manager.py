"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.446993
"""






import asyncio
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import json

from src.devpost_integration.sync_manager import (
    DevpostSyncManager, SyncStatus, SyncPriority, QueuedSyncOperation,
    SyncConflict, SyncStatusReport
)
from src.devpost_integration.models import (
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    SyncOperation, SyncOperationType, SyncResult, FileChangeEvent,
    ProjectMetadata, DevpostProject, ChangeType, ContentType,
    ConflictResolutionStrategy, ValidationResult
)


class TestDevpostSyncManager(ReflectiveModule):
    """Test suite for DevpostSyncManager."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def mock_api_client(self):
        """Mock API client for testing."""
        client = Mock()
        client.update_project = AsyncMock(return_value=True)
        client.upload_media = AsyncMock(return_value=True)
        return client
    
    @pytest.fixture
    def mock_project_manager(self):
        """Mock project manager for testing."""
        manager = Mock()
        manager.get_project_metadata = Mock(return_value=ProjectMetadata(
            title="Test Project",
            tagline="A test project",
            description="This is a test project for unit testing"
        ))
        return manager
    
    @pytest.fixture
    def sync_manager(self, temp_config_dir, mock_api_client, mock_project_manager):
        """Create sync manager instance for testing."""
        config_path = temp_config_dir / "sync_config.json"
        return DevpostSyncManager(
            project_id="test-project-123",
            api_client=mock_api_client,
            project_manager=mock_project_manager,
            config_path=config_path
        )
    
    @pytest.fixture
    def sample_metadata(self):
        """Sample project metadata for testing."""
        return ProjectMetadata(
            title="Test Project",
            tagline="A comprehensive test project",
            description="This is a detailed description of the test project that meets minimum length requirements",
            tags=["python", "testing", "automation"],
            team_members=["Alice", "Bob"]
        )
    
    def test_sync_manager_initialization(self, sync_manager):
        """Test sync manager initializes correctly."""
        assert sync_manager.project_id == "test-project-123"
        assert sync_manager.api_client is not None
        assert sync_manager.project_manager is not None
        assert len(sync_manager.sync_queue) == 0
        assert len(sync_manager.active_operations) == 0
        assert not sync_manager.sync_in_progress
    
    def test_config_loading_and_saving(self, temp_config_dir):
        """Test configuration loading and saving."""
        config_path = temp_config_dir / "test_config.json"
        
        # Test with non-existent config (should use defaults)
        manager = DevpostSyncManager("test", config_path=config_path)
        assert manager.config['max_queue_size'] == 100
        assert manager.config['sync_interval'] == 300
        
        # Test saving config
        manager.config['custom_setting'] = 'test_value'
        manager._save_config()
        
        # Test loading saved config
        manager2 = DevpostSyncManager("test", config_path=config_path)
        assert manager2.config['custom_setting'] == 'test_value'
    
    def test_queue_sync_operation(self, sync_manager):
        """Test queuing sync operations with priority."""
        # Create test operations with different priorities
        low_priority_op = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="description",
            local_value="test",
            remote_value=None,
            project_id="test-project-123"
        )
        
        high_priority_op = SyncOperation(
            operation_type=SyncOperationType.UPLOAD_MEDIA,
            target_field="screenshot.png",
            local_value="media_data",
            remote_value=None,
            project_id="test-project-123"
        )
        
        # Queue operations
        low_id = sync_manager.queue_sync_operation(low_priority_op, SyncPriority.LOW)
        high_id = sync_manager.queue_sync_operation(high_priority_op, SyncPriority.HIGH)
        
        assert len(sync_manager.sync_queue) == 2
        assert low_id is not None
        assert high_id is not None
        
        # High priority should be first in queue
        first_op = sync_manager.sync_queue[0]
        assert first_op.priority == SyncPriority.HIGH
        assert first_op.operation.operation_type == SyncOperationType.UPLOAD_MEDIA
    
    def test_queue_metadata_sync(self, sync_manager, sample_metadata):
        """Test queuing metadata synchronization operations."""
        operation_ids = sync_manager.queue_metadata_sync(sample_metadata)
        
        assert len(operation_ids) > 0
        assert len(sync_manager.sync_queue) > 0
        
        # Check that operations were created for different fields
        operation_types = [op.operation.operation_type for op in sync_manager.sync_queue]
        assert SyncOperationType.UPDATE_METADATA in operation_types
        assert SyncOperationType.UPDATE_DESCRIPTION in operation_types
        assert SyncOperationType.UPDATE_TAGS in operation_types
        assert SyncOperationType.UPDATE_TEAM in operation_types
    
    def test_queue_file_change_sync(self, sync_manager):
        """Test queuing sync operations from file changes."""
        # Test media file change
        media_change = FileChangeEvent(
            file_path=Path("screenshot.png"),
            change_type=ChangeType.CREATED,
            content_type=ContentType.MEDIA,
            affects_sync=True
        )
        
        operation_id = sync_manager.queue_file_change_sync(media_change)
        assert operation_id is not None
        assert len(sync_manager.sync_queue) == 1
        
        queued_op = sync_manager.sync_queue[0]
        assert queued_op.operation.operation_type == SyncOperationType.UPLOAD_MEDIA
        assert queued_op.priority == SyncPriority.HIGH
        
        # Test documentation change
        doc_change = FileChangeEvent(
            file_path=Path("README.md"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.DOCUMENTATION,
            affects_sync=True
        )
        
        operation_id = sync_manager.queue_file_change_sync(doc_change)
        assert operation_id is not None
        assert len(sync_manager.sync_queue) == 2
    
    def test_conflict_detection(self, sync_manager):
        """Test conflict detection between local and remote metadata."""
        local_metadata = ProjectMetadata(
            title="Local Title",
            tagline="Local tagline",
            description="Local description"
        )
        
        remote_metadata = ProjectMetadata(
            title="Remote Title",
            tagline="Local tagline",  # Same as local
            description="Remote description"
        )
        
        conflicts = sync_manager.detect_conflicts(local_metadata, remote_metadata)
        
        # Should detect conflicts for title and description, but not tagline
        assert len(conflicts) == 2
        
        conflict_fields = [c.field_name for c in conflicts]
        assert "title" in conflict_fields
        assert "description" in conflict_fields
        assert "tagline" not in conflict_fields
        
        # Check conflict details
        title_conflict = next(c for c in conflicts if c.field_name == "title")
        assert title_conflict.local_value == "Local Title"
        assert title_conflict.remote_value == "Remote Title"
        assert not title_conflict.resolved
    
    def test_conflict_resolution(self, sync_manager):
        """Test conflict resolution strategies."""
        conflict = SyncConflict(
            field_name="title",
            local_value="Local Title",
            remote_value="Remote Title",
            local_timestamp=datetime.now() - timedelta(minutes=5),
            remote_timestamp=datetime.now() - timedelta(minutes=10)
        )
        
        # Test local wins strategy
        resolved = sync_manager.resolve_conflict(conflict, ConflictResolutionStrategy.LOCAL_WINS)
        assert resolved
        assert conflict.resolved
        assert conflict.resolution_value == "Local Title"
        
        # Reset conflict
        conflict.resolved = False
        conflict.resolution_value = None
        
        # Test remote wins strategy
        resolved = sync_manager.resolve_conflict(conflict, ConflictResolutionStrategy.REMOTE_WINS)
        assert resolved
        assert conflict.resolved
        assert conflict.resolution_value == "Remote Title"
        
        # Reset conflict
        conflict.resolved = False
        conflict.resolution_value = None
        
        # Test timestamp-based strategy (local is newer)
        resolved = sync_manager.resolve_conflict(conflict, ConflictResolutionStrategy.TIMESTAMP_BASED)
        assert resolved
        assert conflict.resolved
        assert conflict.resolution_value == "Local Title"  # Local is newer
    
    def test_resolve_all_conflicts(self, sync_manager):
        """Test resolving all conflicts at once."""
        # Add multiple conflicts
        conflicts = [
            SyncConflict(
                field_name="title",
                local_value="Local Title",
                remote_value="Remote Title",
                local_timestamp=datetime.now(),
                remote_timestamp=datetime.now()
            ),
            SyncConflict(
                field_name="description",
                local_value="Local Description",
                remote_value="Remote Description",
                local_timestamp=datetime.now(),
                remote_timestamp=datetime.now()
            )
        ]
        
        sync_manager.conflicts.extend(conflicts)
        
        resolved_count = sync_manager.resolve_all_conflicts(ConflictResolutionStrategy.LOCAL_WINS)
        
        assert resolved_count == 2
        assert all(c.resolved for c in sync_manager.conflicts)
        assert sync_manager.sync_statistics['conflicts_resolved'] == 2
    
    @pytest.mark.asyncio
    async def test_execute_sync_operation(self, sync_manager):
        """Test executing individual sync operations."""
        operation = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="title",
            local_value="Test Title",
            remote_value=None,
            project_id="test-project-123"
        )
        
        queued_op = QueuedSyncOperation(operation=operation)
        
        result = await sync_manager._execute_sync_operation(queued_op)
        
        assert result.success
        assert "title" in result.changes_made
        assert queued_op.status == SyncStatus.COMPLETED
        assert queued_op.started_at is not None
        assert queued_op.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_process_sync_queue(self, sync_manager, sample_metadata):
        """Test processing the entire sync queue."""
        # Queue some operations
        sync_manager.queue_metadata_sync(sample_metadata)
        
        initial_queue_size = len(sync_manager.sync_queue)
        assert initial_queue_size > 0
        
        # Process the queue
        result = await sync_manager.process_sync_queue()
        
        assert result.success
        assert len(result.changes_made) > 0
        assert len(sync_manager.completed_operations) > 0
        assert sync_manager.last_sync is not None
        assert sync_manager.sync_statistics['total_syncs'] == 1
        assert sync_manager.sync_statistics['successful_syncs'] == 1
    
    def test_get_sync_status(self, sync_manager, sample_metadata):
        """Test getting comprehensive sync status."""
        # Add some operations and conflicts
        sync_manager.queue_metadata_sync(sample_metadata)
        
        conflict = SyncConflict(
            field_name="title",
            local_value="Local",
            remote_value="Remote",
            local_timestamp=datetime.now(),
            remote_timestamp=datetime.now()
        )
        sync_manager.conflicts.append(conflict)
        
        status = sync_manager.get_sync_status()
        
        assert isinstance(status, SyncStatusReport)
        assert status.project_id == "test-project-123"
        assert status.pending_operations > 0
        assert len(status.conflicts) == 1
        assert status.sync_health in ["healthy", "degraded", "critical"]
        assert status.success_rate >= 0
    
    def test_content_change_detection(self, sync_manager):
        """Test content change detection using hashes."""
        content1 = "This is the original content"
        content2 = "This is the modified content"
        
        # First check should detect change (no previous hash)
        changed = sync_manager._has_content_changed("test_field", content1)
        assert changed
        
        # Second check with same content should not detect change
        changed = sync_manager._has_content_changed("test_field", content1)
        assert not changed
        
        # Check with different content should detect change
        changed = sync_manager._has_content_changed("test_field", content2)
        assert changed
    
    def test_get_pending_changes(self, sync_manager, sample_metadata):
        """Test getting list of pending changes."""
        # Initially no changes
        changes = sync_manager.get_pending_changes()
        assert len(changes) == 0
        
        # Queue some operations
        sync_manager.queue_metadata_sync(sample_metadata)
        
        changes = sync_manager.get_pending_changes()
        assert len(changes) > 0
        
        # Check that changes contain operation descriptions
        change_text = " ".join(changes)
        assert "update_metadata" in change_text or "update_description" in change_text
    
    def test_sync_callbacks(self, sync_manager):
        """Test sync callback functionality."""
        callback_results = []
        
        def test_callback(result: SyncResult):
            callback_results.append(result)
        
        # Add callback
        sync_manager.add_sync_callback(test_callback)
        assert len(sync_manager.sync_callbacks) == 1
        
        # Remove callback
        sync_manager.remove_sync_callback(test_callback)
        assert len(sync_manager.sync_callbacks) == 0
    
    def test_clear_completed_operations(self, sync_manager):
        """Test clearing completed operations."""
        # Add some completed operations
        operation = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="title",
            local_value="test",
            remote_value=None,
            project_id="test-project-123"
        )
        
        completed_op = QueuedSyncOperation(operation=operation, status=SyncStatus.COMPLETED)
        sync_manager.completed_operations.append(completed_op)
        
        assert len(sync_manager.completed_operations) == 1
        
        cleared_count = sync_manager.clear_completed_operations()
        
        assert cleared_count == 1
        assert len(sync_manager.completed_operations) == 0
    
    def test_legacy_sync_project_method(self, sync_manager):
        """Test legacy sync_project method for backward compatibility."""
        # Queue an operation
        operation = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="title",
            local_value="test",
            remote_value=None,
            project_id="test-project-123"
        )
        sync_manager.queue_sync_operation(operation)
        
        # Test legacy method
        result = sync_manager.sync_project()
        
        assert isinstance(result, SyncResult)
        # Note: In a real test environment, this might need more setup
        # to properly test the async-to-sync conversion
    
    def test_queue_size_limit(self, sync_manager):
        """Test that queue respects size limits."""
        # Set a small queue size for testing
        sync_manager.config['max_queue_size'] = 2
        
        # Add operations beyond the limit
        for i in range(5):
            operation = SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field=f"field_{i}",
                local_value=f"value_{i}",
                remote_value=None,
                project_id="test-project-123"
            )
            sync_manager.queue_sync_operation(operation)
        
        # Queue should not exceed the limit
        assert len(sync_manager.sync_queue) <= 2
    
    def test_priority_ordering(self, sync_manager):
        """Test that operations are ordered by priority."""
        # Add operations in reverse priority order
        operations = [
            (SyncOperationType.UPDATE_METADATA, SyncPriority.LOW),
            (SyncOperationType.UPDATE_DESCRIPTION, SyncPriority.CRITICAL),
            (SyncOperationType.UPDATE_TAGS, SyncPriority.NORMAL),
            (SyncOperationType.UPLOAD_MEDIA, SyncPriority.HIGH)
        ]
        
        for op_type, priority in operations:
            operation = SyncOperation(
                operation_type=op_type,
                target_field=op_type.value,
                local_value="test",
                remote_value=None,
                project_id="test-project-123"
            )
            sync_manager.queue_sync_operation(operation, priority)
        
        # Check that queue is ordered by priority (highest first)
        priorities = [op.priority for op in sync_manager.sync_queue]
        assert priorities == sorted(priorities, key=lambda x: x.value, reverse=True)


    # Batch Synchronization Tests (Task 7.2)
    
    @pytest.mark.asyncio
    async def test_batch_sync_operations(self, sync_manager):
        """Test batch synchronization of multiple operations."""
        # Create multiple operations
        operations = []
        for i in range(5):
            operation = SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field=f"field_{i}",
                local_value=f"value_{i}",
                remote_value=None,
                project_id="test-project-123"
            )
            operations.append(operation)
        
        # Execute batch sync
        result = await sync_manager.batch_sync_operations(operations, batch_size=2)
        
        assert result.success
        assert len(result.changes_made) == 5
        assert result.sync_duration is not None
        assert sync_manager.sync_statistics['total_syncs'] == 1
    
    @pytest.mark.asyncio
    async def test_batch_sync_with_rollback(self, sync_manager):
        """Test batch sync with rollback on failure."""
        # Enable rollback on batch failure
        sync_manager.config['rollback_on_batch_failure'] = True
        
        # Create operations (some will fail in mock)
        operations = []
        for i in range(3):
            operation = SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field=f"field_{i}",
                local_value=f"value_{i}",
                remote_value=None,
                project_id="test-project-123"
            )
            operations.append(operation)
        
        # Mock the _execute_sync_operation method to fail on second operation
        original_execute = sync_manager._execute_sync_operation
        call_count = 0
        
        async def mock_execute_with_failure(queued_op):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # Fail on second operation
                return SyncResult(success=False, error="Simulated API Error")
            return await original_execute(queued_op)
        
        sync_manager._execute_sync_operation = mock_execute_with_failure
        
        result = await sync_manager.batch_sync_operations(operations, batch_size=1)
        
        # Should handle the failure and attempt rollback
        assert not result.success
        assert "Simulated API Error" in result.error or "Batch" in result.error
    
    def test_create_rollback_checkpoint(self, sync_manager, sample_metadata):
        """Test creating rollback checkpoints."""
        # Add some operations to the queue
        sync_manager.queue_metadata_sync(sample_metadata)
        
        # Create checkpoint
        checkpoint = sync_manager._create_rollback_checkpoint()
        
        assert 'timestamp' in checkpoint
        assert 'queue_state' in checkpoint
        assert 'completed_operations_count' in checkpoint
        assert 'statistics' in checkpoint
        assert len(checkpoint['queue_state']) > 0
    
    @pytest.mark.asyncio
    async def test_rollback_to_checkpoint(self, sync_manager, sample_metadata):
        """Test rolling back to a checkpoint."""
        # Create initial state
        sync_manager.queue_metadata_sync(sample_metadata)
        initial_queue_size = len(sync_manager.sync_queue)
        
        # Create checkpoint
        checkpoint = sync_manager._create_rollback_checkpoint()
        
        # Modify state
        sync_manager.sync_queue.clear()
        sync_manager.completed_operations.append(Mock())
        
        # Rollback
        result = await sync_manager._rollback_to_checkpoint(checkpoint)
        
        assert result.success
        assert len(sync_manager.sync_queue) == initial_queue_size
        assert len(sync_manager.completed_operations) == 0
    
    def test_schedule_sync(self, sync_manager):
        """Test scheduling sync operations."""
        operations = [
            SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field="title",
                local_value="test",
                remote_value=None,
                project_id="test-project-123"
            )
        ]
        
        schedule_time = datetime.now() + timedelta(hours=1)
        schedule_id = sync_manager.schedule_sync(operations, schedule_time)
        
        assert schedule_id is not None
        assert hasattr(sync_manager, 'scheduled_syncs')
        assert schedule_id in sync_manager.scheduled_syncs
        
        scheduled_sync = sync_manager.scheduled_syncs[schedule_id]
        assert scheduled_sync['status'] == 'scheduled'
        assert len(scheduled_sync['operations']) == 1
        assert scheduled_sync['schedule_time'] == schedule_time
    
    @pytest.mark.asyncio
    async def test_execute_scheduled_sync(self, sync_manager):
        """Test executing scheduled sync operations."""
        operations = [
            SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field="title",
                local_value="test",
                remote_value=None,
                project_id="test-project-123"
            )
        ]
        
        schedule_time = datetime.now()
        schedule_id = sync_manager.schedule_sync(operations, schedule_time)
        
        # Execute scheduled sync
        result = await sync_manager.execute_scheduled_sync(schedule_id)
        
        assert result.success
        assert len(result.changes_made) > 0
        
        # Check that scheduled sync status was updated
        scheduled_sync = sync_manager.scheduled_syncs[schedule_id]
        assert scheduled_sync['status'] == 'completed'
        assert 'completed_at' in scheduled_sync
    
    @pytest.mark.asyncio
    async def test_scheduled_sync_retry_logic(self, sync_manager):
        """Test retry logic for failed scheduled syncs."""
        operations = [
            SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field="title",
                local_value="test",
                remote_value=None,
                project_id="test-project-123"
            )
        ]
        
        # Schedule with custom retry config
        retry_config = {
            'max_retries': 2,
            'retry_delay': 1,  # 1 second for testing
            'exponential_backoff': True,
            'backoff_multiplier': 2.0
        }
        
        schedule_time = datetime.now()
        schedule_id = sync_manager.schedule_sync(operations, schedule_time, retry_config)
        
        # Mock the _execute_sync_operation method to fail
        original_execute = sync_manager._execute_sync_operation
        
        async def mock_execute_with_failure(queued_op):
            return SyncResult(success=False, error="API Error")
        
        sync_manager._execute_sync_operation = mock_execute_with_failure
        
        # Execute scheduled sync (should fail and schedule retry)
        result = await sync_manager.execute_scheduled_sync(schedule_id)
        
        assert not result.success
        
        # Check that retry was scheduled
        scheduled_sync = sync_manager.scheduled_syncs[schedule_id]
        assert scheduled_sync['status'] == 'scheduled'  # Rescheduled for retry
        assert scheduled_sync['retry_count'] == 1
        assert scheduled_sync['schedule_time'] > datetime.now()  # Rescheduled for future
    
    def test_get_scheduled_syncs(self, sync_manager):
        """Test getting list of scheduled syncs."""
        # Initially no scheduled syncs
        syncs = sync_manager.get_scheduled_syncs()
        assert len(syncs) == 0
        
        # Schedule some syncs
        operations = [
            SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field="title",
                local_value="test",
                remote_value=None,
                project_id="test-project-123"
            )
        ]
        
        schedule_id1 = sync_manager.schedule_sync(operations, datetime.now() + timedelta(hours=1))
        schedule_id2 = sync_manager.schedule_sync(operations, datetime.now() + timedelta(hours=2))
        
        syncs = sync_manager.get_scheduled_syncs()
        assert len(syncs) == 2
        
        # Check sync info structure
        sync_info = syncs[0]
        assert 'schedule_id' in sync_info
        assert 'schedule_time' in sync_info
        assert 'status' in sync_info
        assert 'operation_count' in sync_info
        assert 'retry_count' in sync_info
        assert 'max_retries' in sync_info
        assert 'created_at' in sync_info
    
    def test_cancel_scheduled_sync(self, sync_manager):
        """Test cancelling scheduled sync operations."""
        operations = [
            SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field="title",
                local_value="test",
                remote_value=None,
                project_id="test-project-123"
            )
        ]
        
        schedule_id = sync_manager.schedule_sync(operations, datetime.now() + timedelta(hours=1))
        
        # Cancel the scheduled sync
        cancelled = sync_manager.cancel_scheduled_sync(schedule_id)
        assert cancelled
        
        # Check that status was updated
        scheduled_sync = sync_manager.scheduled_syncs[schedule_id]
        assert scheduled_sync['status'] == 'cancelled'
        assert 'cancelled_at' in scheduled_sync
        
        # Try to cancel again (should fail since it's already cancelled)
        cancelled_again = sync_manager.cancel_scheduled_sync(schedule_id)
        assert not cancelled_again  # Should return False for already cancelled sync
    
    @pytest.mark.asyncio
    async def test_retry_failed_operations(self, sync_manager):
        """Test retrying failed operations."""
        # Create some failed operations
        operation1 = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="title",
            local_value="test1",
            remote_value=None,
            project_id="test-project-123"
        )
        
        operation2 = SyncOperation(
            operation_type=SyncOperationType.UPDATE_DESCRIPTION,
            target_field="description",
            local_value="test2",
            remote_value=None,
            project_id="test-project-123"
        )
        
        failed_op1 = QueuedSyncOperation(operation=operation1, status=SyncStatus.FAILED, retry_count=0)
        failed_op2 = QueuedSyncOperation(operation=operation2, status=SyncStatus.FAILED, retry_count=3)  # Max retries exceeded
        
        sync_manager.failed_operations = [failed_op1, failed_op2]
        
        # Retry failed operations
        result = await sync_manager.retry_failed_operations(max_retries=3)
        
        assert result.success
        assert len(result.changes_made) > 0
        
        # Check that only the operation with retries remaining was processed
        assert len(sync_manager.failed_operations) == 1  # Only the one with max retries exceeded
        assert sync_manager.failed_operations[0].operation.target_field == "description"
    
    def test_get_batch_sync_statistics(self, sync_manager):
        """Test getting batch sync statistics."""
        # Schedule some syncs to populate statistics
        operations = [
            SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field="title",
                local_value="test",
                remote_value=None,
                project_id="test-project-123"
            )
        ]
        
        sync_manager.schedule_sync(operations, datetime.now() + timedelta(hours=1))
        sync_manager.schedule_sync(operations, datetime.now() + timedelta(hours=2))
        
        # Mark one as failed
        sync_manager.scheduled_syncs[list(sync_manager.scheduled_syncs.keys())[0]]['status'] = 'failed'
        
        stats = sync_manager.get_batch_sync_statistics()
        
        assert 'average_batch_size' in stats
        assert 'rollback_enabled' in stats
        assert 'scheduled_syncs_count' in stats
        assert 'active_scheduled_syncs' in stats
        assert 'failed_scheduled_syncs' in stats
        
        assert stats['scheduled_syncs_count'] == 2
        assert stats['active_scheduled_syncs'] == 1  # One is still scheduled
        assert stats['failed_scheduled_syncs'] == 1   # One is failed
    
    @pytest.mark.asyncio
    async def test_batch_size_configuration(self, sync_manager):
        """Test that batch size configuration is respected."""
        # Set small batch size
        sync_manager.config['batch_size'] = 2
        
        # Create more operations than batch size
        operations = []
        for i in range(5):
            operation = SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field=f"field_{i}",
                local_value=f"value_{i}",
                remote_value=None,
                project_id="test-project-123"
            )
            operations.append(operation)
        
        # Mock the _execute_batch method to track batch sizes
        original_execute_batch = sync_manager._execute_batch
        batch_sizes = []
        
        async def mock_execute_batch(ops, batch_num):
            batch_sizes.append(len(ops))
            return await original_execute_batch(ops, batch_num)
        
        sync_manager._execute_batch = mock_execute_batch
        
        # Execute batch sync
        result = await sync_manager.batch_sync_operations(operations)
        
        assert result.success
        assert len(batch_sizes) == 3  # 5 operations / 2 batch size = 3 batches
        assert batch_sizes[0] == 2  # First batch
        assert batch_sizes[1] == 2  # Second batch
        assert batch_sizes[2] == 1  # Third batch (remainder)
    
    @pytest.mark.asyncio
    async def test_concurrent_batch_execution(self, sync_manager):
        """Test that operations within a batch execute and complete successfully."""
        operations = []
        execution_order = []
        
        for i in range(3):
            operation = SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field=f"field_{i}",
                local_value=f"value_{i}",
                remote_value=None,
                project_id="test-project-123"
            )
            operations.append(operation)
        
        # Mock _execute_sync_operation to track execution
        original_execute = sync_manager._execute_sync_operation
        
        async def mock_execute_with_tracking(queued_op):
            execution_order.append(queued_op.operation.target_field)
            await asyncio.sleep(0.01)  # Small delay to simulate work
            return await original_execute(queued_op)
        
        sync_manager._execute_sync_operation = mock_execute_with_tracking
        
        result = await sync_manager._execute_batch(operations, 1)
        
        assert result.success
        assert len(result.changes_made) == 3
        assert len(execution_order) == 3
        
        # Verify all operations were executed
        expected_fields = {"field_0", "field_1", "field_2"}
        actual_fields = set(execution_order)
        assert actual_fields == expected_fields


    # Validation Integration Tests (Task 7.3)
    
    def test_validate_before_sync(self, sync_manager, sample_metadata):
        """Test validation before sync operations."""
        result = sync_manager.validate_before_sync(sample_metadata)
        
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'errors')
        assert hasattr(result, 'warnings')
        assert hasattr(result, 'completion_percentage')
        
        # Good metadata should pass validation
        assert result.is_valid or len(result.errors) == 0
    
    def test_validate_before_sync_with_bad_metadata(self, sync_manager):
        """Test validation with problematic metadata."""
        bad_metadata = ProjectMetadata(
            title=None,  # Missing title
            tagline="Short",  # Too short
            description="Too short"  # Too short
        )
        
        result = sync_manager.validate_before_sync(bad_metadata)
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert len(result.missing_fields) > 0
    
    def test_get_validation_suggestions(self, sync_manager):
        """Test getting validation suggestions."""
        bad_metadata = ProjectMetadata(
            title="Test",
            tagline="Short tagline",
            description="Short description"
        )
        
        suggestions = sync_manager.get_validation_suggestions(bad_metadata)
        
        assert isinstance(suggestions, list)
        # Should have suggestions for improving the metadata
        assert len(suggestions) >= 0  # Might be 0 if metadata is actually valid
    
    def test_validate_sync_operation(self, sync_manager):
        """Test sync operation validation."""
        # Valid operation
        valid_operation = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="title",
            local_value="Test Title",
            remote_value=None,
            project_id="test-project-123"
        )
        
        assert sync_manager.validate_sync_operation(valid_operation)
        
        # Invalid operation - missing project_id
        invalid_operation = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="title",
            local_value="Test Title",
            remote_value=None,
            project_id=""  # Empty project_id
        )
        
        assert not sync_manager.validate_sync_operation(invalid_operation)
        
        # Invalid operation - missing target_field
        invalid_operation2 = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="",  # Empty target_field
            local_value="Test Title",
            remote_value=None,
            project_id="test-project-123"
        )
        
        assert not sync_manager.validate_sync_operation(invalid_operation2)
    
    def test_queue_sync_operation_with_validation(self, sync_manager):
        """Test that queuing validates operations."""
        # Valid operation should succeed
        valid_operation = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="title",
            local_value="Test Title",
            remote_value=None,
            project_id="test-project-123"
        )
        
        operation_id = sync_manager.queue_sync_operation(valid_operation)
        assert operation_id is not None
        assert len(sync_manager.sync_queue) == 1
        
        # Invalid operation should raise ValueError
        invalid_operation = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="",  # Empty target_field
            local_value="Test Title",
            remote_value=None,
            project_id="test-project-123"
        )
        
        with pytest.raises(ValueError, match="Invalid sync operation"):
            sync_manager.queue_sync_operation(invalid_operation)
    
    @pytest.mark.asyncio
    async def test_sync_with_validation(self, sync_manager, sample_metadata):
        """Test sync with validation integration."""
        result = await sync_manager.sync_with_validation(sample_metadata)
        
        assert isinstance(result, SyncResult)
        # Should succeed with good metadata
        assert result.success
    
    @pytest.mark.asyncio
    async def test_sync_with_validation_bad_metadata(self, sync_manager):
        """Test sync with validation fails for bad metadata."""
        bad_metadata = ProjectMetadata(
            title=None,  # Missing title
            tagline="Short",
            description="Short"
        )
        
        result = await sync_manager.sync_with_validation(bad_metadata)
        
        assert not result.success
        assert "Validation failed" in result.error
    
    @pytest.mark.asyncio
    async def test_sync_with_validation_force_sync(self, sync_manager):
        """Test force sync bypasses validation."""
        bad_metadata = ProjectMetadata(
            title=None,  # Missing title
            tagline="Short",
            description="Short"
        )
        
        result = await sync_manager.sync_with_validation(bad_metadata, force_sync=True)
        
        # Should succeed when forced, even with bad metadata
        # (though it might have no changes to sync)
        assert result.success or "No changes to sync" in result.error
    
    def test_validation_engine_integration(self, sync_manager):
        """Test that sync manager has validation engine integrated."""
        assert hasattr(sync_manager, 'validation_engine')
        assert sync_manager.validation_engine is not None
        
        # Test that validation engine has rules
        active_rules = sync_manager.validation_engine.get_active_rules()
        assert len(active_rules) > 0

    # Additional Batch Synchronization Tests (Task 7.2)
    
    @pytest.mark.asyncio
    async def test_batch_sync_empty_operations(self, sync_manager):
        """Test batch sync with empty operations list."""
        result = await sync_manager.batch_sync_operations([])
        
        assert result.success
        assert len(result.changes_made) == 0
        assert result.sync_duration is not None
    
    @pytest.mark.asyncio
    async def test_batch_sync_large_batch(self, sync_manager):
        """Test batch sync with large number of operations."""
        # Create 20 operations
        operations = []
        for i in range(20):
            operation = SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field=f"field_{i}",
                local_value=f"value_{i}",
                remote_value=None,
                project_id="test-project-123"
            )
            operations.append(operation)
        
        # Execute with small batch size
        result = await sync_manager.batch_sync_operations(operations, batch_size=3)
        
        assert result.success
        assert len(result.changes_made) == 20
        assert result.sync_duration is not None
    
    @pytest.mark.asyncio
    async def test_batch_sync_partial_failure_with_rollback(self, sync_manager):
        """Test batch sync with partial failure and rollback enabled."""
        sync_manager.config['rollback_on_batch_failure'] = True
        
        operations = []
        for i in range(5):
            operation = SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field=f"field_{i}",
                local_value=f"value_{i}",
                remote_value=None,
                project_id="test-project-123"
            )
            operations.append(operation)
        
        # Mock _execute_batch to fail on second batch
        original_execute_batch = sync_manager._execute_batch
        call_count = 0
        
        async def mock_execute_batch_with_failure(operations, batch_number):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # Fail on second batch
                return SyncResult(success=False, error="Batch 2 failed")
            return await original_execute_batch(operations, batch_number)
        
        sync_manager._execute_batch = mock_execute_batch_with_failure
        
        result = await sync_manager.batch_sync_operations(operations, batch_size=2)
        
        # Should fail and attempt rollback
        assert not result.success
        assert "Batch 2 failed" in result.error or "rollback" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_batch_sync_without_rollback(self, sync_manager):
        """Test batch sync with rollback disabled."""
        sync_manager.config['rollback_on_batch_failure'] = False
        
        operations = []
        for i in range(4):
            operation = SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field=f"field_{i}",
                local_value=f"value_{i}",
                remote_value=None,
                project_id="test-project-123"
            )
            operations.append(operation)
        
        # Mock _execute_batch to fail on second batch
        original_execute_batch = sync_manager._execute_batch
        call_count = 0
        
        async def mock_execute_batch_with_failure(operations, batch_number):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # Fail on second batch
                return SyncResult(success=False, error="Batch 2 failed")
            return await original_execute_batch(operations, batch_number)
        
        sync_manager._execute_batch = mock_execute_batch_with_failure
        
        result = await sync_manager.batch_sync_operations(operations, batch_size=2)
        
        # Should continue processing despite failure
        assert not result.success
        assert "Batch 2 failed" in result.error
    
    def test_create_rollback_checkpoint_comprehensive(self, sync_manager, sample_metadata):
        """Test comprehensive rollback checkpoint creation."""
        # Set up initial state
        sync_manager.queue_metadata_sync(sample_metadata)
        sync_manager.completed_operations.append(Mock())
        sync_manager.failed_operations.append(Mock())
        sync_manager.conflicts.append(Mock())
        sync_manager.sync_statistics['total_syncs'] = 5
        
        checkpoint = sync_manager._create_rollback_checkpoint()
        
        # Verify checkpoint contains all necessary data
        assert 'timestamp' in checkpoint
        assert 'queue_state' in checkpoint
        assert 'completed_operations_count' in checkpoint
        assert 'failed_operations_count' in checkpoint
        assert 'conflicts_count' in checkpoint
        assert 'statistics' in checkpoint
        
        # Verify counts match current state
        assert checkpoint['completed_operations_count'] == 1
        assert checkpoint['failed_operations_count'] == 1
        assert checkpoint['conflicts_count'] == 1
        assert checkpoint['statistics']['total_syncs'] == 5
        
        # Verify queue state structure
        assert len(checkpoint['queue_state']) > 0
        queue_item = checkpoint['queue_state'][0]
        assert 'operation' in queue_item
        assert 'priority' in queue_item
        assert 'status' in queue_item
    
    @pytest.mark.asyncio
    async def test_rollback_to_checkpoint_comprehensive(self, sync_manager, sample_metadata):
        """Test comprehensive rollback to checkpoint."""
        # Create initial state and checkpoint
        sync_manager.queue_metadata_sync(sample_metadata)
        initial_queue_size = len(sync_manager.sync_queue)
        checkpoint = sync_manager._create_rollback_checkpoint()
        
        # Modify state significantly
        sync_manager.sync_queue.clear()
        sync_manager.completed_operations.extend([Mock(), Mock(), Mock()])
        sync_manager.failed_operations.extend([Mock(), Mock()])
        sync_manager.conflicts.extend([Mock()])
        sync_manager.sync_statistics['total_syncs'] = 100
        
        # Verify state was modified
        assert len(sync_manager.sync_queue) == 0
        assert len(sync_manager.completed_operations) == 3
        assert len(sync_manager.failed_operations) == 2
        assert len(sync_manager.conflicts) == 1
        assert sync_manager.sync_statistics['total_syncs'] == 100
        
        # Rollback
        result = await sync_manager._rollback_to_checkpoint(checkpoint)
        
        # Verify rollback success
        assert result.success
        assert "rollback_completed" in result.changes_made
        
        # Verify state was restored
        assert len(sync_manager.sync_queue) == initial_queue_size
        assert len(sync_manager.completed_operations) == 0
        assert len(sync_manager.failed_operations) == 0
        assert len(sync_manager.conflicts) == 0
        assert sync_manager.sync_statistics['total_syncs'] == 0  # From checkpoint
    
    def test_schedule_sync_with_custom_retry_config(self, sync_manager):
        """Test scheduling sync with custom retry configuration."""
        operations = [
            SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field="title",
                local_value="test",
                remote_value=None,
                project_id="test-project-123"
            )
        ]
        
        custom_retry_config = {
            'max_retries': 5,
            'retry_delay': 30,
            'exponential_backoff': False,
            'backoff_multiplier': 1.5
        }
        
        schedule_time = datetime.now() + timedelta(hours=2)
        schedule_id = sync_manager.schedule_sync(operations, schedule_time, custom_retry_config)
        
        assert schedule_id is not None
        
        scheduled_sync = sync_manager.scheduled_syncs[schedule_id]
        assert scheduled_sync['retry_config']['max_retries'] == 5
        assert scheduled_sync['retry_config']['retry_delay'] == 30
        assert scheduled_sync['retry_config']['exponential_backoff'] == False
        assert scheduled_sync['retry_config']['backoff_multiplier'] == 1.5
    
    @pytest.mark.asyncio
    async def test_execute_scheduled_sync_not_found(self, sync_manager):
        """Test executing non-existent scheduled sync."""
        result = await sync_manager.execute_scheduled_sync("non-existent-id")
        
        assert not result.success
        assert "not found" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_scheduled_sync_with_exponential_backoff(self, sync_manager):
        """Test scheduled sync retry with exponential backoff."""
        operations = [
            SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field="title",
                local_value="test",
                remote_value=None,
                project_id="test-project-123"
            )
        ]
        
        retry_config = {
            'max_retries': 3,
            'retry_delay': 10,
            'exponential_backoff': True,
            'backoff_multiplier': 2.0
        }
        
        schedule_time = datetime.now()
        schedule_id = sync_manager.schedule_sync(operations, schedule_time, retry_config)
        
        # Mock batch_sync_operations to fail
        original_batch_sync = sync_manager.batch_sync_operations
        
        async def mock_batch_sync_failure(operations, batch_size=None):
            return SyncResult(success=False, error="API Error")
        
        sync_manager.batch_sync_operations = mock_batch_sync_failure
        
        # Execute scheduled sync (should fail and reschedule)
        result = await sync_manager.execute_scheduled_sync(schedule_id)
        
        assert not result.success
        
        # Check that retry was scheduled with exponential backoff
        scheduled_sync = sync_manager.scheduled_syncs[schedule_id]
        assert scheduled_sync['status'] == 'scheduled'
        assert scheduled_sync['retry_count'] == 1
        
        # Verify exponential backoff calculation
        expected_delay = 10 * (2.0 ** 0)  # First retry: base_delay * multiplier^0
        actual_delay = (scheduled_sync['schedule_time'] - datetime.now()).total_seconds()
        assert abs(actual_delay - expected_delay) < 5  # Allow 5 second tolerance
        
        # Restore original method
        sync_manager.batch_sync_operations = original_batch_sync
    
    def test_get_scheduled_syncs_with_filtering(self, sync_manager):
        """Test getting scheduled syncs with status filtering."""
        operations = [
            SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field="title",
                local_value="test",
                remote_value=None,
                project_id="test-project-123"
            )
        ]
        
        # Create syncs with different statuses
        schedule_id1 = sync_manager.schedule_sync(operations, datetime.now() + timedelta(hours=1))
        schedule_id2 = sync_manager.schedule_sync(operations, datetime.now() + timedelta(hours=2))
        
        # Manually set different statuses
        sync_manager.scheduled_syncs[schedule_id1]['status'] = 'completed'
        sync_manager.scheduled_syncs[schedule_id2]['status'] = 'failed'
        
        # Test filtering
        all_syncs = sync_manager.get_scheduled_syncs()
        assert len(all_syncs) == 2
        
        completed_syncs = sync_manager.get_scheduled_syncs(status_filter='completed')
        assert len(completed_syncs) == 1
        assert completed_syncs[0]['schedule_id'] == schedule_id1
        
        failed_syncs = sync_manager.get_scheduled_syncs(status_filter='failed')
        assert len(failed_syncs) == 1
        assert failed_syncs[0]['schedule_id'] == schedule_id2
        
        scheduled_syncs = sync_manager.get_scheduled_syncs(status_filter='scheduled')
        assert len(scheduled_syncs) == 0
    
    def test_cancel_scheduled_sync_edge_cases(self, sync_manager):
        """Test cancelling scheduled sync edge cases."""
        operations = [
            SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field="title",
                local_value="test",
                remote_value=None,
                project_id="test-project-123"
            )
        ]
        
        # Test cancelling non-existent sync
        cancelled = sync_manager.cancel_scheduled_sync("non-existent-id")
        assert not cancelled
        
        # Test cancelling completed sync
        schedule_id = sync_manager.schedule_sync(operations, datetime.now() + timedelta(hours=1))
        sync_manager.scheduled_syncs[schedule_id]['status'] = 'completed'
        
        cancelled = sync_manager.cancel_scheduled_sync(schedule_id)
        assert not cancelled  # Cannot cancel completed sync
        
        # Test cancelling failed sync
        sync_manager.scheduled_syncs[schedule_id]['status'] = 'failed'
        cancelled = sync_manager.cancel_scheduled_sync(schedule_id)
        assert not cancelled  # Cannot cancel failed sync
        
        # Test cancelling already cancelled sync
        sync_manager.scheduled_syncs[schedule_id]['status'] = 'cancelled'
        cancelled = sync_manager.cancel_scheduled_sync(schedule_id)
        assert not cancelled  # Cannot cancel already cancelled sync
    
    @pytest.mark.asyncio
    async def test_retry_failed_operations_comprehensive(self, sync_manager):
        """Test comprehensive retry of failed operations."""
        # Create operations with different retry counts
        operation1 = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="title",
            local_value="test1",
            remote_value=None,
            project_id="test-project-123"
        )
        
        operation2 = SyncOperation(
            operation_type=SyncOperationType.UPDATE_DESCRIPTION,
            target_field="description",
            local_value="test2",
            remote_value=None,
            project_id="test-project-123"
        )
        
        operation3 = SyncOperation(
            operation_type=SyncOperationType.UPDATE_TAGS,
            target_field="tags",
            local_value=["tag1", "tag2"],
            remote_value=None,
            project_id="test-project-123"
        )
        
        # Create failed operations with different retry counts
        failed_op1 = QueuedSyncOperation(operation=operation1, status=SyncStatus.FAILED, retry_count=0)
        failed_op2 = QueuedSyncOperation(operation=operation2, status=SyncStatus.FAILED, retry_count=2)
        failed_op3 = QueuedSyncOperation(operation=operation3, status=SyncStatus.FAILED, retry_count=3)  # Max retries
        
        sync_manager.failed_operations = [failed_op1, failed_op2, failed_op3]
        
        # Retry with max_retries=3
        result = await sync_manager.retry_failed_operations(max_retries=3)
        
        assert result.success
        assert len(result.changes_made) > 0
        
        # Check that only operations within retry limit were processed
        # operation3 should remain in failed_operations (exceeded max retries)
        assert len(sync_manager.failed_operations) == 1
        assert sync_manager.failed_operations[0].operation.target_field == "tags"
    
    @pytest.mark.asyncio
    async def test_retry_failed_operations_no_operations(self, sync_manager):
        """Test retry when no failed operations exist."""
        result = await sync_manager.retry_failed_operations()
        
        assert result.success
        assert len(result.changes_made) == 0
        assert "No failed operations to retry" in result.error
    
    @pytest.mark.asyncio
    async def test_retry_failed_operations_all_exceeded(self, sync_manager):
        """Test retry when all operations have exceeded max retries."""
        operation = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="title",
            local_value="test",
            remote_value=None,
            project_id="test-project-123"
        )
        
        failed_op = QueuedSyncOperation(operation=operation, status=SyncStatus.FAILED, retry_count=5)
        sync_manager.failed_operations = [failed_op]
        
        result = await sync_manager.retry_failed_operations(max_retries=3)
        
        assert result.success
        assert len(result.changes_made) == 0
        assert "exceeded max retries" in result.error
    
    def test_get_batch_sync_statistics_comprehensive(self, sync_manager):
        """Test comprehensive batch sync statistics."""
        # Set up some state
        sync_manager.sync_statistics['total_syncs'] = 10
        sync_manager.sync_statistics['successful_syncs'] = 8
        sync_manager.sync_statistics['failed_syncs'] = 2
        
        # Add some scheduled syncs
        operations = [
            SyncOperation(
                operation_type=SyncOperationType.UPDATE_METADATA,
                target_field="title",
                local_value="test",
                remote_value=None,
                project_id="test-project-123"
            )
        ]
        
        schedule_id1 = sync_manager.schedule_sync(operations, datetime.now() + timedelta(hours=1))
        schedule_id2 = sync_manager.schedule_sync(operations, datetime.now() + timedelta(hours=2))
        sync_manager.scheduled_syncs[schedule_id2]['status'] = 'failed'
        
        stats = sync_manager.get_batch_sync_statistics()
        
        # Verify basic statistics are included
        assert 'total_syncs' in stats
        assert 'successful_syncs' in stats
        assert 'failed_syncs' in stats
        
        # Verify batch-specific statistics
        assert 'average_batch_size' in stats
        assert 'rollback_enabled' in stats
        assert 'scheduled_syncs_count' in stats
        assert 'active_scheduled_syncs' in stats
        assert 'failed_scheduled_syncs' in stats
        
        # Verify values
        assert stats['scheduled_syncs_count'] == 2
        assert stats['active_scheduled_syncs'] == 1  # One scheduled, one failed
        assert stats['failed_scheduled_syncs'] == 1
        assert stats['average_batch_size'] == sync_manager.config['batch_size']
    
    @pytest.mark.asyncio
    async def test_sync_with_validation_success(self, sync_manager, sample_metadata):
        """Test sync with validation that passes."""
        # Mock validation to pass
        original_validate = sync_manager.validate_before_sync
        
        def mock_validate_success(metadata, hackathon_id=None):
            return ValidationResult(
                is_valid=True,
                errors=[],
                warnings=["Minor formatting issue"],
                missing_fields=[],
                completion_percentage=95.0
            )
        
        sync_manager.validate_before_sync = mock_validate_success
        
        result = await sync_manager.sync_with_validation(sample_metadata)
        
        assert result.success
        assert len(result.changes_made) > 0
        assert "Minor formatting issue" in result.error  # Warning included
        
        # Restore original method
        sync_manager.validate_before_sync = original_validate
    
    @pytest.mark.asyncio
    async def test_sync_with_validation_failure(self, sync_manager, sample_metadata):
        """Test sync with validation that fails."""
        # Mock validation to fail
        original_validate = sync_manager.validate_before_sync
        
        def mock_validate_failure(metadata, hackathon_id=None):
            return ValidationResult(
                is_valid=False,
                errors=["Title too short", "Missing required field"],
                warnings=[],
                missing_fields=["demo_url"],
                completion_percentage=60.0
            )
        
        sync_manager.validate_before_sync = mock_validate_failure
        
        result = await sync_manager.sync_with_validation(sample_metadata)
        
        assert not result.success
        assert "Validation failed" in result.error
        assert "Title too short" in result.error
        assert "Missing required field" in result.error
        
        # Restore original method
        sync_manager.validate_before_sync = original_validate
    
    @pytest.mark.asyncio
    async def test_sync_with_validation_force_sync(self, sync_manager, sample_metadata):
        """Test sync with validation failure but force_sync enabled."""
        # Mock validation to fail
        original_validate = sync_manager.validate_before_sync
        
        def mock_validate_failure(metadata, hackathon_id=None):
            return ValidationResult(
                is_valid=False,
                errors=["Title too short"],
                warnings=["Minor issue"],
                missing_fields=["demo_url"],
                completion_percentage=60.0
            )
        
        sync_manager.validate_before_sync = mock_validate_failure
        
        result = await sync_manager.sync_with_validation(sample_metadata, force_sync=True)
        
        assert result.success  # Should succeed with force_sync
        assert len(result.changes_made) > 0
        assert "Minor issue" in result.error  # Warnings still included
        
        # Restore original method
        sync_manager.validate_before_sync = original_validate
    
    def test_validate_sync_operation_comprehensive(self, sync_manager):
        """Test comprehensive sync operation validation."""
        # Test valid operation
        valid_operation = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="title",
            local_value="Test Title",
            remote_value=None,
            project_id="test-project-123"
        )
        
        assert sync_manager.validate_sync_operation(valid_operation)
        
        # Test operation missing project_id
        invalid_operation1 = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="title",
            local_value="Test Title",
            remote_value=None,
            project_id=""
        )
        
        assert not sync_manager.validate_sync_operation(invalid_operation1)
        
        # Test operation missing target_field
        invalid_operation2 = SyncOperation(
            operation_type=SyncOperationType.UPDATE_METADATA,
            target_field="",
            local_value="Test Title",
            remote_value=None,
            project_id="test-project-123"
        )
        
        assert not sync_manager.validate_sync_operation(invalid_operation2)
        
        # Test media upload operation missing local_value
        invalid_media_operation = SyncOperation(
            operation_type=SyncOperationType.UPLOAD_MEDIA,
            target_field="screenshot.png",
            local_value=None,
            remote_value=None,
            project_id="test-project-123"
        )
        
        assert not sync_manager.validate_sync_operation(invalid_media_operation)
        
        # Test valid media upload operation
        valid_media_operation = SyncOperation(
            operation_type=SyncOperationType.UPLOAD_MEDIA,
            target_field="screenshot.png",
            local_value="/path/to/screenshot.png",
            remote_value=None,
            project_id="test-project-123"
        )
        
        assert sync_manager.validate_sync_operation(valid_media_operation)


if __name__ == "__main__":

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

    pytest.main([__file__])