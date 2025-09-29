"""
Full system integration tests for AI Memory Palace.

Tests the complete system working together including:
- Context management with Observatory integration
- Tracing system integration
- Multi-project management
- Backup and recovery
- Security and privacy
"""

import pytest
import asyncio
import tempfile
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.beast_mode.ai_memory_palace.context_manager import ContextManager
from src.beast_mode.ai_memory_palace.context_registry import ContextRegistry
from src.beast_mode.ai_memory_palace.context_engine import ContextEngine
from src.beast_mode.ai_memory_palace.context_validator import ContextValidator
from src.beast_mode.ai_memory_palace.storage import ContextStorage
from src.beast_mode.ai_memory_palace.models import (
    SessionContext, ContextEvent, ContextEventType, ProjectState,
    Decision, WorkItem, SystemDiscovery
)
from src.beast_mode.ai_memory_palace.backup_recovery import ContextBackupManager, BackupType
from src.beast_mode.ai_memory_palace.multi_project_manager import MultiProjectContextManager, ProjectDetector
from src.beast_mode.ai_memory_palace.security import ContextSecurity
from src.beast_mode.ai_memory_palace.developer_tools import ContextInspector


class TestFullSystemIntegration:
    """Integration tests for the complete AI Memory Palace system"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create sample project structure
            (workspace / "python_project").mkdir()
            (workspace / "python_project" / "requirements.txt").write_text("pytest>=7.0.0\n")
            (workspace / "python_project" / "main.py").write_text("print('Hello World')\n")
            
            (workspace / "js_project").mkdir()
            (workspace / "js_project" / "package.json").write_text('{"name": "test", "version": "1.0.0"}\n')
            (workspace / "js_project" / "index.js").write_text("console.log('Hello World');\n")
            
            (workspace / "kiro_project").mkdir()
            (workspace / "kiro_project" / ".kiro").mkdir()
            (workspace / "kiro_project" / ".kiro" / "specs").mkdir()
            
            yield workspace
    
    @pytest.fixture
    def full_system(self, temp_workspace):
        """Create complete AI Memory Palace system"""
        # Storage layer
        storage_dir = temp_workspace / ".kiro" / "context_storage"
        storage = ContextStorage(storage_dir)
        
        # Core components
        registry = ContextRegistry(storage)
        validator = ContextValidator()
        engine = ContextEngine()
        security = ContextSecurity()
        
        # Management components
        context_manager = ContextManager(registry)
        backup_manager = ContextBackupManager(storage, validator)
        multi_project_manager = MultiProjectContextManager(registry, security)
        
        # Developer tools
        inspector = ContextInspector(context_manager, registry, validator)
        
        return {
            'storage': storage,
            'registry': registry,
            'validator': validator,
            'engine': engine,
            'security': security,
            'context_manager': context_manager,
            'backup_manager': backup_manager,
            'multi_project_manager': multi_project_manager,
            'inspector': inspector,
            'workspace': temp_workspace
        }
    
    def test_complete_session_workflow(self, full_system):
        """Test complete session workflow from start to finish"""
        system = full_system
        
        # 1. Project Detection and Setup
        detector = ProjectDetector()
        projects = detector.detect_projects(system['workspace'])
        
        assert len(projects) >= 3  # python, js, kiro projects
        
        # Register projects
        for project in projects:
            system['multi_project_manager'].register_project(project)
        
        # 2. Start session for Python project
        python_project = next(p for p in projects if p.project_type.value == "python")
        session_id = system['context_manager'].start_session(python_project.project_id)
        
        assert session_id is not None
        
        # 3. Add conversation events
        events = [
            ("user", "I want to add a new feature to this Python project"),
            ("ai", "I can help you with that. What kind of feature are you looking to add?"),
            ("user", "A REST API using FastAPI"),
            ("ai", "Great choice! Let me help you set up FastAPI. First, let's add it to requirements.txt")
        ]
        
        for role, content in events:
            event_type = ContextEventType.USER_MESSAGE if role == "user" else ContextEventType.AI_RESPONSE
            system['context_manager'].add_conversation_event(event_type, content)
        
        # 4. Record decisions and work
        decision = Decision(
            decision_id="use_fastapi",
            description="Use FastAPI for REST API implementation",
            rationale="FastAPI provides automatic OpenAPI docs and good performance",
            timestamp=datetime.now(),
            context={"framework": "fastapi", "reason": "performance_and_docs"}
        )
        
        work_item = WorkItem(
            work_id="setup_fastapi",
            work_type="dependency_addition",
            description="Add FastAPI to requirements.txt",
            timestamp=datetime.now(),
            files_created=[],
            files_modified=["requirements.txt"],
            outcome="success"
        )
        
        # Add to context (would normally be done through context manager methods)
        context = system['context_manager'].get_current_context()
        context.decisions_made.append(decision)
        context.work_completed.append(work_item)
        
        # 5. Update project state
        new_state = ProjectState(
            current_directory=str(python_project.root_path),
            running_services=[],
            recent_changes=["requirements.txt"],
            environment_variables={"PYTHONPATH": str(python_project.root_path)},
            git_status={"branch": "feature/fastapi", "status": "modified"}
        )
        
        system['context_manager'].update_project_state(new_state)
        
        # 6. Create backup
        backup_metadata = system['backup_manager'].create_backup(
            python_project.project_id, 
            backup_type=BackupType.MANUAL
        )
        
        assert backup_metadata is not None
        assert backup_metadata.validation_status == "valid"
        
        # 7. Validate context integrity
        validation_result = system['validator'].validate_context_integrity(context)
        assert validation_result.is_valid
        
        # 8. Test context inspection
        inspection = system['inspector'].inspect_context(python_project.project_id)
        
        assert inspection["basic_info"]["project_id"] == python_project.project_id
        assert inspection["content_analysis"]["conversation_events"] == 4
        assert inspection["content_analysis"]["decisions_made"] == 1
        assert inspection["content_analysis"]["work_items"] == 1
        
        # 9. End session
        success = system['context_manager'].end_session()
        assert success is True
        
        # 10. Restore session and verify persistence
        success = system['context_manager'].restore_session(python_project.project_id, session_id)
        assert success is True
        
        restored_context = system['context_manager'].get_current_context()
        assert len(restored_context.conversation_history) == 4
        assert len(restored_context.decisions_made) == 1
        assert len(restored_context.work_completed) == 1
        assert restored_context.project_state.git_status["branch"] == "feature/fastapi"
    
    def test_multi_project_context_isolation(self, full_system):
        """Test context isolation between multiple projects"""
        system = full_system
        
        # Detect and register projects
        detector = ProjectDetector()
        projects = detector.detect_projects(system['workspace'])
        
        for project in projects:
            system['multi_project_manager'].register_project(project)
        
        # Get different project types
        python_project = next(p for p in projects if p.project_type.value == "python")
        js_project = next(p for p in projects if p.project_type.value == "javascript")
        
        # Start sessions for both projects
        python_session = system['context_manager'].start_session(python_project.project_id)
        system['context_manager'].add_conversation_event(
            ContextEventType.USER_MESSAGE, 
            "Python project conversation"
        )
        system['context_manager'].end_session()
        
        js_session = system['context_manager'].start_session(js_project.project_id)
        system['context_manager'].add_conversation_event(
            ContextEventType.USER_MESSAGE, 
            "JavaScript project conversation"
        )
        system['context_manager'].end_session()
        
        # Verify isolation - Python project context
        system['context_manager'].restore_session(python_project.project_id, python_session)
        python_context = system['context_manager'].get_current_context()
        
        assert python_context.project_id == python_project.project_id
        assert len(python_context.conversation_history) == 1
        assert "Python project" in python_context.conversation_history[0].content
        
        system['context_manager'].end_session()
        
        # Verify isolation - JavaScript project context
        system['context_manager'].restore_session(js_project.project_id, js_session)
        js_context = system['context_manager'].get_current_context()
        
        assert js_context.project_id == js_project.project_id
        assert len(js_context.conversation_history) == 1
        assert "JavaScript project" in js_context.conversation_history[0].content
        
        # Contexts should be completely separate
        assert python_context.session_id != js_context.session_id
        assert python_context.conversation_history[0].content != js_context.conversation_history[0].content
    
    def test_backup_and_recovery_workflow(self, full_system):
        """Test complete backup and recovery workflow"""
        system = full_system
        
        # Setup project and context
        detector = ProjectDetector()
        projects = detector.detect_projects(system['workspace'])
        python_project = next(p for p in projects if p.project_type.value == "python")
        
        system['multi_project_manager'].register_project(python_project)
        
        # Create rich context
        session_id = system['context_manager'].start_session(python_project.project_id)
        
        # Add multiple conversation events
        for i in range(10):
            system['context_manager'].add_conversation_event(
                ContextEventType.USER_MESSAGE, 
                f"Message {i}: Working on feature implementation"
            )
            system['context_manager'].add_conversation_event(
                ContextEventType.AI_RESPONSE, 
                f"Response {i}: Here's how to implement that feature"
            )
        
        # Create multiple backups
        backup1 = system['backup_manager'].create_backup(
            python_project.project_id, 
            backup_type=BackupType.MANUAL
        )
        
        # Add more content
        system['context_manager'].add_conversation_event(
            ContextEventType.USER_MESSAGE, 
            "Additional content after first backup"
        )
        
        backup2 = system['backup_manager'].create_backup(
            python_project.project_id, 
            backup_type=BackupType.AUTOMATIC
        )
        
        assert backup1 is not None
        assert backup2 is not None
        assert backup1.backup_id != backup2.backup_id
        
        # Simulate context corruption
        context = system['context_manager'].get_current_context()
        original_conversation_count = len(context.conversation_history)
        
        # Clear context to simulate corruption
        system['context_manager'].clear_context("CONFIRM_CLEAR_CONTEXT")
        
        # Verify context is cleared
        cleared_context = system['context_manager'].get_current_context()
        assert len(cleared_context.conversation_history) == 0
        
        # Restore from backup
        restore_success = system['backup_manager'].restore_context(backup2.backup_id)
        assert restore_success is True
        
        # Verify restoration
        system['context_manager'].restore_session(python_project.project_id, session_id)
        restored_context = system['context_manager'].get_current_context()
        
        assert len(restored_context.conversation_history) == original_conversation_count
        assert "Additional content after first backup" in restored_context.conversation_history[-1].content
    
    def test_context_engine_processing(self, full_system):
        """Test context engine processing and optimization"""
        system = full_system
        
        # Setup project
        detector = ProjectDetector()
        projects = detector.detect_projects(system['workspace'])
        python_project = next(p for p in projects if p.project_type.value == "python")
        
        system['multi_project_manager'].register_project(python_project)
        session_id = system['context_manager'].start_session(python_project.project_id)
        
        # Create large context for processing
        for i in range(100):
            system['context_manager'].add_conversation_event(
                ContextEventType.USER_MESSAGE, 
                f"User message {i}: " + "x" * 1000  # Large content
            )
            system['context_manager'].add_conversation_event(
                ContextEventType.AI_RESPONSE, 
                f"AI response {i}: " + "y" * 1000  # Large content
            )
        
        context = system['context_manager'].get_current_context()
        original_size = context.get_context_size()
        
        # Process context through engine
        processed_context = system['engine'].process_context_for_storage(context)
        
        # Should be processed (potentially compressed/summarized)
        assert processed_context is not None
        assert processed_context.project_id == context.project_id
        
        # Test relevance filtering
        relevant_events = system['engine'].filter_relevant_events(
            context.conversation_history, 
            "implementation"
        )
        
        # Should find relevant events
        assert len(relevant_events) > 0
    
    def test_security_and_privacy_integration(self, full_system):
        """Test security and privacy features integration"""
        system = full_system
        
        # Setup project
        detector = ProjectDetector()
        projects = detector.detect_projects(system['workspace'])
        python_project = next(p for p in projects if p.project_type.value == "python")
        
        system['multi_project_manager'].register_project(python_project)
        session_id = system['context_manager'].start_session(python_project.project_id)
        
        # Add content with sensitive information
        sensitive_content = [
            "My API key is sk-1234567890abcdef",
            "The password is mySecretPassword123",
            "Email: user@example.com, Phone: 555-123-4567",
            "Credit card: 4111-1111-1111-1111"
        ]
        
        for content in sensitive_content:
            system['context_manager'].add_conversation_event(
                ContextEventType.USER_MESSAGE, 
                content
            )
        
        context = system['context_manager'].get_current_context()
        
        # Test sensitive data detection
        sensitive_data = system['security'].detect_sensitive_data(context)
        
        assert len(sensitive_data) > 0
        assert any("api_key" in item["type"] for item in sensitive_data)
        assert any("password" in item["type"] for item in sensitive_data)
        
        # Test data redaction
        redacted_context = system['security'].redact_sensitive_data(context)
        
        # Verify redaction occurred
        redacted_content = " ".join([event.content for event in redacted_context.conversation_history])
        assert "sk-1234567890abcdef" not in redacted_content
        assert "mySecretPassword123" not in redacted_content
        assert "[REDACTED" in redacted_content
    
    def test_concurrent_multi_project_operations(self, full_system):
        """Test concurrent operations across multiple projects"""
        system = full_system
        
        # Setup multiple projects
        detector = ProjectDetector()
        projects = detector.detect_projects(system['workspace'])
        
        for project in projects:
            system['multi_project_manager'].register_project(project)
        
        results = {}
        errors = []
        
        def project_worker(project):
            try:
                # Start session
                session_id = system['context_manager'].start_session(project.project_id)
                
                # Add events
                for i in range(20):
                    system['context_manager'].add_conversation_event(
                        ContextEventType.USER_MESSAGE, 
                        f"Message {i} for {project.project_name}"
                    )
                    time.sleep(0.01)  # Small delay to simulate real usage
                
                # Create backup
                backup = system['backup_manager'].create_backup(project.project_id)
                
                # Get final context
                context = system['context_manager'].get_current_context()
                
                results[project.project_id] = {
                    'session_id': session_id,
                    'events': len(context.conversation_history),
                    'backup_created': backup is not None,
                    'context_size': context.get_context_size()
                }
                
                system['context_manager'].end_session()
                
            except Exception as e:
                errors.append(f"Project {project.project_id}: {e}")
        
        # Start concurrent workers
        threads = []
        for project in projects[:3]:  # Limit to 3 projects for test speed
            thread = threading.Thread(target=project_worker, args=(project,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 3
        
        for project_id, result in results.items():
            assert result['events'] == 20
            assert result['backup_created'] is True
            assert result['context_size'] > 0
    
    def test_system_health_monitoring(self, full_system):
        """Test system health monitoring across all components"""
        system = full_system
        
        # Check health of all components
        health_checks = {
            'context_manager': system['context_manager'].health_check(),
            'backup_manager': system['backup_manager'].health_check(),
            'multi_project_manager': system['multi_project_manager'].health_check(),
            'storage': system['storage'].health_check(),
            'registry': system['registry'].health_check()
        }
        
        # All components should be healthy
        for component, health in health_checks.items():
            assert health['status'] in ['healthy', 'degraded'], f"{component} is unhealthy: {health}"
        
        # Test system under load
        detector = ProjectDetector()
        projects = detector.detect_projects(system['workspace'])
        python_project = next(p for p in projects if p.project_type.value == "python")
        
        system['multi_project_manager'].register_project(python_project)
        session_id = system['context_manager'].start_session(python_project.project_id)
        
        # Add load
        for i in range(50):
            system['context_manager'].add_conversation_event(
                ContextEventType.USER_MESSAGE, 
                f"Load test message {i}"
            )
        
        # Check health under load
        loaded_health = system['context_manager'].health_check()
        assert loaded_health['status'] in ['healthy', 'degraded']
        
        # Verify metrics are being tracked
        assert 'metrics' in loaded_health
        assert loaded_health['metrics']['active_sessions'] >= 0
    
    def test_error_recovery_and_resilience(self, full_system):
        """Test system error recovery and resilience"""
        system = full_system
        
        # Setup project
        detector = ProjectDetector()
        projects = detector.detect_projects(system['workspace'])
        python_project = next(p for p in projects if p.project_type.value == "python")
        
        system['multi_project_manager'].register_project(python_project)
        session_id = system['context_manager'].start_session(python_project.project_id)
        
        # Add initial content
        system['context_manager'].add_conversation_event(
            ContextEventType.USER_MESSAGE, 
            "Initial content before error"
        )
        
        # Create backup
        backup = system['backup_manager'].create_backup(python_project.project_id)
        
        # Simulate storage error by temporarily breaking storage
        original_store = system['storage'].store_context
        system['storage'].store_context = Mock(side_effect=Exception("Storage error"))
        
        # Try to add content during error
        event_id = system['context_manager'].add_conversation_event(
            ContextEventType.USER_MESSAGE, 
            "Content during error"
        )
        
        # Should handle error gracefully
        assert event_id is None or isinstance(event_id, str)
        
        # Restore storage
        system['storage'].store_context = original_store
        
        # System should recover
        recovery_event_id = system['context_manager'].add_conversation_event(
            ContextEventType.USER_MESSAGE, 
            "Content after recovery"
        )
        
        assert recovery_event_id is not None
        
        # Verify system state
        context = system['context_manager'].get_current_context()
        assert context is not None
        assert len(context.conversation_history) >= 1  # At least initial content
    
    def test_performance_under_load(self, full_system):
        """Test system performance under load"""
        system = full_system
        
        # Setup project
        detector = ProjectDetector()
        projects = detector.detect_projects(system['workspace'])
        python_project = next(p for p in projects if p.project_type.value == "python")
        
        system['multi_project_manager'].register_project(python_project)
        
        # Measure session start time
        start_time = time.time()
        session_id = system['context_manager'].start_session(python_project.project_id)
        session_start_time = time.time() - start_time
        
        assert session_start_time < 1.0  # Should start within 1 second
        
        # Measure event addition performance
        event_times = []
        for i in range(100):
            start_time = time.time()
            system['context_manager'].add_conversation_event(
                ContextEventType.USER_MESSAGE, 
                f"Performance test message {i}"
            )
            event_times.append(time.time() - start_time)
        
        # Average event time should be reasonable
        avg_event_time = sum(event_times) / len(event_times)
        assert avg_event_time < 0.1  # Should add events within 100ms on average
        
        # Measure context retrieval time
        start_time = time.time()
        context = system['context_manager'].get_current_context()
        retrieval_time = time.time() - start_time
        
        assert retrieval_time < 0.5  # Should retrieve within 500ms
        assert len(context.conversation_history) == 100
        
        # Measure backup creation time
        start_time = time.time()
        backup = system['backup_manager'].create_backup(python_project.project_id)
        backup_time = time.time() - start_time
        
        assert backup_time < 2.0  # Should backup within 2 seconds
        assert backup is not None
    
    def test_data_consistency_across_operations(self, full_system):
        """Test data consistency across all system operations"""
        system = full_system
        
        # Setup project
        detector = ProjectDetector()
        projects = detector.detect_projects(system['workspace'])
        python_project = next(p for p in projects if p.project_type.value == "python")
        
        system['multi_project_manager'].register_project(python_project)
        session_id = system['context_manager'].start_session(python_project.project_id)
        
        # Add structured content
        events_added = []
        for i in range(10):
            event_id = system['context_manager'].add_conversation_event(
                ContextEventType.USER_MESSAGE, 
                f"Consistency test message {i}"
            )
            events_added.append(event_id)
        
        # Verify all events were added
        context = system['context_manager'].get_current_context()
        assert len(context.conversation_history) == 10
        
        # Create backup and verify consistency
        backup = system['backup_manager'].create_backup(python_project.project_id)
        assert backup.validation_status == "valid"
        
        # Validate context integrity
        validation_result = system['validator'].validate_context_integrity(context)
        assert validation_result.is_valid
        
        # End and restore session
        system['context_manager'].end_session()
        system['context_manager'].restore_session(python_project.project_id, session_id)
        
        # Verify consistency after restore
        restored_context = system['context_manager'].get_current_context()
        assert len(restored_context.conversation_history) == 10
        
        # Verify event IDs are consistent
        restored_event_ids = [event.event_id for event in restored_context.conversation_history]
        assert all(event_id in restored_event_ids for event_id in events_added if event_id)
        
        # Verify timestamps are in order
        timestamps = [event.timestamp for event in restored_context.conversation_history]
        assert timestamps == sorted(timestamps)
        
        # Verify project state consistency
        assert restored_context.project_id == python_project.project_id
        assert restored_context.session_id == session_id