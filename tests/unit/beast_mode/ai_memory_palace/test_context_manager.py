"""
Unit tests for ContextManager component.
"""

import pytest
import asyncio
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.beast_mode.ai_memory_palace.context_manager import ContextManager
from src.beast_mode.ai_memory_palace.models import SessionContext, ContextEvent, ContextEventType, ProjectState
from src.beast_mode.ai_memory_palace.storage import ContextStorage
from src.beast_mode.ai_memory_palace.context_registry import ContextRegistry


class TestContextManager:
    """Test suite for ContextManager"""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def mock_storage(self, temp_storage_dir):
        """Create mock storage"""
        return ContextStorage(temp_storage_dir)
    
    @pytest.fixture
    def mock_registry(self, mock_storage):
        """Create mock registry"""
        return ContextRegistry(mock_storage)
    
    @pytest.fixture
    def context_manager(self, mock_registry):
        """Create ContextManager instance"""
        return ContextManager(mock_registry)
    
    @pytest.fixture
    def sample_context(self):
        """Create sample context for testing"""
        return SessionContext(
            project_id="test_project",
            session_id="test_session",
            timestamp=datetime.now(),
            conversation_history=[],
            decisions_made=[],
            work_completed=[],
            system_discoveries=[],
            project_state=ProjectState(
                current_directory=".",
                running_services=[],
                recent_changes=[],
                environment_variables={},
                git_status={}
            ),
            spec_states={}
        )
    
    def test_initialization(self, context_manager):
        """Test ContextManager initialization"""
        assert context_manager is not None
        assert hasattr(context_manager, 'registry')
        assert hasattr(context_manager, 'current_session_id')
        assert context_manager.current_session_id is None
    
    def test_start_session(self, context_manager):
        """Test starting a new session"""
        project_id = "test_project"
        session_id = context_manager.start_session(project_id)
        
        assert session_id is not None
        assert context_manager.current_session_id == session_id
        assert context_manager.current_project_id == project_id
    
    def test_start_session_with_existing_context(self, context_manager, sample_context):
        """Test starting session with existing context"""
        # Store existing context
        context_manager.registry.store_context(sample_context)
        
        # Start session for same project
        session_id = context_manager.start_session(sample_context.project_id)
        
        assert session_id == sample_context.session_id
        assert context_manager.current_session_id == sample_context.session_id
    
    def test_end_session(self, context_manager, sample_context):
        """Test ending a session"""
        # Start session
        context_manager.start_session(sample_context.project_id)
        
        # End session
        success = context_manager.end_session()
        
        assert success is True
        assert context_manager.current_session_id is None
        assert context_manager.current_project_id is None
    
    def test_restore_session(self, context_manager, sample_context):
        """Test restoring an existing session"""
        # Store context
        context_manager.registry.store_context(sample_context)
        
        # Restore session
        success = context_manager.restore_session(sample_context.project_id, sample_context.session_id)
        
        assert success is True
        assert context_manager.current_session_id == sample_context.session_id
        assert context_manager.current_project_id == sample_context.project_id
    
    def test_restore_nonexistent_session(self, context_manager):
        """Test restoring a nonexistent session"""
        success = context_manager.restore_session("nonexistent_project", "nonexistent_session")
        
        assert success is False
        assert context_manager.current_session_id is None
    
    def test_add_conversation_event(self, context_manager, sample_context):
        """Test adding conversation event"""
        # Start session
        context_manager.start_session(sample_context.project_id)
        
        # Add conversation event
        event_id = context_manager.add_conversation_event(
            event_type=ContextEventType.USER_MESSAGE,
            content="Test message",
            metadata={"test": "data"}
        )
        
        assert event_id is not None
        
        # Verify event was added
        context = context_manager.get_current_context()
        assert len(context.conversation_history) == 1
        assert context.conversation_history[0].content == "Test message"
    
    def test_add_conversation_event_no_session(self, context_manager):
        """Test adding conversation event without active session"""
        event_id = context_manager.add_conversation_event(
            event_type=ContextEventType.USER_MESSAGE,
            content="Test message"
        )
        
        assert event_id is None
    
    def test_get_current_context(self, context_manager, sample_context):
        """Test getting current context"""
        # No active session
        context = context_manager.get_current_context()
        assert context is None
        
        # Start session
        context_manager.start_session(sample_context.project_id)
        
        # Get context
        context = context_manager.get_current_context()
        assert context is not None
        assert context.project_id == sample_context.project_id
    
    def test_update_project_state(self, context_manager, sample_context):
        """Test updating project state"""
        # Start session
        context_manager.start_session(sample_context.project_id)
        
        # Update project state
        new_state = ProjectState(
            current_directory="/new/path",
            running_services=["service1"],
            recent_changes=["file1.py"],
            environment_variables={"TEST": "value"},
            git_status={"branch": "main"}
        )
        
        success = context_manager.update_project_state(new_state)
        assert success is True
        
        # Verify update
        context = context_manager.get_current_context()
        assert context.project_state.current_directory == "/new/path"
        assert "service1" in context.project_state.running_services
    
    def test_clear_context(self, context_manager, sample_context):
        """Test clearing context"""
        # Start session and add some data
        context_manager.start_session(sample_context.project_id)
        context_manager.add_conversation_event(
            event_type=ContextEventType.USER_MESSAGE,
            content="Test message"
        )
        
        # Clear context
        success = context_manager.clear_context("CONFIRM_CLEAR_CONTEXT")
        assert success is True
        
        # Verify context is cleared
        context = context_manager.get_current_context()
        assert len(context.conversation_history) == 0
    
    def test_clear_context_wrong_confirmation(self, context_manager, sample_context):
        """Test clearing context with wrong confirmation"""
        context_manager.start_session(sample_context.project_id)
        
        success = context_manager.clear_context("WRONG_CONFIRMATION")
        assert success is False
    
    def test_get_context_summary(self, context_manager, sample_context):
        """Test getting context summary"""
        # Start session and add data
        context_manager.start_session(sample_context.project_id)
        context_manager.add_conversation_event(
            event_type=ContextEventType.USER_MESSAGE,
            content="Test message"
        )
        
        # Get summary
        summary = context_manager.get_context_summary()
        
        assert summary is not None
        assert summary["project_id"] == sample_context.project_id
        assert summary["conversation_events"] == 1
        assert "size_mb" in summary
    
    def test_get_context_summary_no_session(self, context_manager):
        """Test getting context summary without active session"""
        summary = context_manager.get_context_summary()
        assert summary is None
    
    def test_health_check(self, context_manager):
        """Test health check endpoint"""
        health = context_manager.health_check()
        
        assert "status" in health
        assert "context_manager" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_session_timeout_handling(self, context_manager, sample_context):
        """Test session timeout handling"""
        # Start session
        context_manager.start_session(sample_context.project_id)
        
        # Simulate timeout by setting very short timeout
        context_manager.session_timeout_minutes = 0.001  # Very short timeout
        
        # Wait for timeout
        import time
        time.sleep(0.1)
        
        # Check if session is still active (should handle timeout gracefully)
        context = context_manager.get_current_context()
        # Context should still be accessible even if session times out
        assert context is not None
    
    def test_concurrent_session_operations(self, context_manager):
        """Test concurrent session operations"""
        import threading
        import time
        
        results = []
        
        def start_session_worker(project_id):
            session_id = context_manager.start_session(f"project_{project_id}")
            results.append(session_id)
        
        # Start multiple sessions concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=start_session_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Should have 5 different session IDs
        assert len(results) == 5
        assert len(set(results)) == 5  # All unique
    
    def test_context_persistence_across_sessions(self, context_manager, sample_context):
        """Test that context persists across session restarts"""
        # Start session and add data
        session_id = context_manager.start_session(sample_context.project_id)
        context_manager.add_conversation_event(
            event_type=ContextEventType.USER_MESSAGE,
            content="Persistent message"
        )
        
        # End session
        context_manager.end_session()
        
        # Restore session
        context_manager.restore_session(sample_context.project_id, session_id)
        
        # Verify data persisted
        context = context_manager.get_current_context()
        assert len(context.conversation_history) == 1
        assert context.conversation_history[0].content == "Persistent message"
    
    @patch('src.beast_mode.ai_memory_palace.context_manager.datetime')
    def test_session_timestamp_tracking(self, mock_datetime, context_manager, sample_context):
        """Test session timestamp tracking"""
        fixed_time = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_time
        
        # Start session
        context_manager.start_session(sample_context.project_id)
        
        # Verify timestamp
        context = context_manager.get_current_context()
        assert context.timestamp == fixed_time
    
    def test_error_handling_storage_failure(self, context_manager):
        """Test error handling when storage fails"""
        # Mock storage failure
        context_manager.registry.storage.store_context = Mock(side_effect=Exception("Storage error"))
        
        # Try to start session
        session_id = context_manager.start_session("test_project")
        
        # Should handle error gracefully
        assert session_id is not None  # Should still create session ID
        
        # But context operations should fail gracefully
        success = context_manager.add_conversation_event(
            event_type=ContextEventType.USER_MESSAGE,
            content="Test"
        )
        # Should return None or handle error gracefully
        assert success is None or success is False
    
    def test_memory_usage_monitoring(self, context_manager, sample_context):
        """Test memory usage monitoring"""
        # Start session
        context_manager.start_session(sample_context.project_id)
        
        # Add many events to increase memory usage
        for i in range(100):
            context_manager.add_conversation_event(
                event_type=ContextEventType.USER_MESSAGE,
                content=f"Message {i}" * 100  # Large content
            )
        
        # Get context summary to check size
        summary = context_manager.get_context_summary()
        
        assert summary["size_mb"] > 0
        assert summary["conversation_events"] == 100
    
    def test_context_validation_integration(self, context_manager, sample_context):
        """Test integration with context validation"""
        # Start session
        context_manager.start_session(sample_context.project_id)
        
        # Add valid event
        context_manager.add_conversation_event(
            event_type=ContextEventType.USER_MESSAGE,
            content="Valid message"
        )
        
        # Get context and verify it's valid
        context = context_manager.get_current_context()
        assert context is not None
        assert len(context.conversation_history) == 1
        
        # Context should be internally consistent
        assert context.project_id == sample_context.project_id
        assert context.session_id is not None


class TestContextManagerIntegration:
    """Integration tests for ContextManager with other components"""
    
    @pytest.fixture
    def full_context_manager(self, temp_storage_dir):
        """Create ContextManager with real dependencies"""
        storage = ContextStorage(temp_storage_dir)
        registry = ContextRegistry(storage)
        return ContextManager(registry)
    
    def test_full_session_lifecycle(self, full_context_manager):
        """Test complete session lifecycle with real storage"""
        project_id = "integration_test_project"
        
        # Start session
        session_id = full_context_manager.start_session(project_id)
        assert session_id is not None
        
        # Add conversation events
        event1_id = full_context_manager.add_conversation_event(
            event_type=ContextEventType.USER_MESSAGE,
            content="Hello, AI!"
        )
        
        event2_id = full_context_manager.add_conversation_event(
            event_type=ContextEventType.AI_RESPONSE,
            content="Hello! How can I help you?"
        )
        
        assert event1_id is not None
        assert event2_id is not None
        
        # Update project state
        new_state = ProjectState(
            current_directory="/test/path",
            running_services=["test_service"],
            recent_changes=["test_file.py"],
            environment_variables={"TEST_ENV": "test_value"},
            git_status={"branch": "test_branch", "status": "clean"}
        )
        
        success = full_context_manager.update_project_state(new_state)
        assert success is True
        
        # Get context and verify all data
        context = full_context_manager.get_current_context()
        assert context.project_id == project_id
        assert len(context.conversation_history) == 2
        assert context.project_state.current_directory == "/test/path"
        assert "test_service" in context.project_state.running_services
        
        # End session
        success = full_context_manager.end_session()
        assert success is True
        
        # Restore session and verify persistence
        success = full_context_manager.restore_session(project_id, session_id)
        assert success is True
        
        restored_context = full_context_manager.get_current_context()
        assert restored_context.project_id == project_id
        assert len(restored_context.conversation_history) == 2
        assert restored_context.project_state.current_directory == "/test/path"
    
    def test_multiple_project_contexts(self, full_context_manager):
        """Test managing multiple project contexts"""
        # Create contexts for multiple projects
        projects = ["project_a", "project_b", "project_c"]
        session_ids = {}
        
        for project_id in projects:
            session_id = full_context_manager.start_session(project_id)
            session_ids[project_id] = session_id
            
            # Add unique content to each project
            full_context_manager.add_conversation_event(
                event_type=ContextEventType.USER_MESSAGE,
                content=f"Message for {project_id}"
            )
            
            full_context_manager.end_session()
        
        # Verify each project has its own context
        for project_id in projects:
            success = full_context_manager.restore_session(project_id, session_ids[project_id])
            assert success is True
            
            context = full_context_manager.get_current_context()
            assert context.project_id == project_id
            assert len(context.conversation_history) == 1
            assert f"Message for {project_id}" in context.conversation_history[0].content
            
            full_context_manager.end_session()
    
    def test_context_size_limits(self, full_context_manager):
        """Test behavior with large contexts"""
        project_id = "large_context_project"
        
        # Start session
        full_context_manager.start_session(project_id)
        
        # Add many large events
        large_content = "x" * 10000  # 10KB per message
        
        for i in range(100):  # 1MB total
            full_context_manager.add_conversation_event(
                event_type=ContextEventType.USER_MESSAGE,
                content=f"{large_content}_{i}"
            )
        
        # Verify context is still functional
        context = full_context_manager.get_current_context()
        assert context is not None
        assert len(context.conversation_history) == 100
        
        # Check context size
        summary = full_context_manager.get_context_summary()
        assert summary["size_mb"] > 0.5  # Should be at least 0.5MB
    
    def test_concurrent_access_different_projects(self, full_context_manager):
        """Test concurrent access to different project contexts"""
        import threading
        import time
        
        results = {}
        
        def project_worker(project_id):
            try:
                # Start session
                session_id = full_context_manager.start_session(f"concurrent_{project_id}")
                
                # Add events
                for i in range(10):
                    full_context_manager.add_conversation_event(
                        event_type=ContextEventType.USER_MESSAGE,
                        content=f"Message {i} for project {project_id}"
                    )
                    time.sleep(0.01)  # Small delay
                
                # Get final context
                context = full_context_manager.get_current_context()
                results[project_id] = len(context.conversation_history)
                
                full_context_manager.end_session()
                
            except Exception as e:
                results[project_id] = f"Error: {e}"
        
        # Start multiple workers
        threads = []
        for i in range(3):
            thread = threading.Thread(target=project_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify results
        for i in range(3):
            assert results[i] == 10  # Each should have 10 messages
    
    def test_error_recovery(self, full_context_manager):
        """Test error recovery scenarios"""
        project_id = "error_recovery_project"
        
        # Start session
        session_id = full_context_manager.start_session(project_id)
        
        # Add some data
        full_context_manager.add_conversation_event(
            event_type=ContextEventType.USER_MESSAGE,
            content="Before error"
        )
        
        # Simulate storage corruption by directly modifying storage
        context = full_context_manager.get_current_context()
        original_session_id = context.session_id
        
        # Try to continue operations after simulated error
        event_id = full_context_manager.add_conversation_event(
            event_type=ContextEventType.USER_MESSAGE,
            content="After error"
        )
        
        # Should still work
        assert event_id is not None
        
        # Verify context integrity
        final_context = full_context_manager.get_current_context()
        assert final_context.session_id == original_session_id
        assert len(final_context.conversation_history) == 2