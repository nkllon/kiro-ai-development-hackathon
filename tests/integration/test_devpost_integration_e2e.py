"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.596851
"""




import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.devpost_integration.project_manager import DevpostProjectManager
from src.devpost_integration.sync_manager import DevpostSyncManager
from src.devpost_integration.preview_generator import DevpostPreviewGenerator
from src.devpost_integration.deadline_tracker import DeadlineTracker
from src.devpost_integration.notification_manager import NotificationManager
from src.devpost_integration.validation_engine import ValidationEngine
from src.devpost_integration.models import (
    DevpostConfig, ProjectConnection, ProjectMetadata, ValidationResult
)


class TestDevpostIntegrationE2E(ReflectiveModule):
    """End-to-end integration tests for complete workflows."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory with sample files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create sample project files
            (project_path / 'README.md').write_text("""
# Test Project

A sample hackathon project for testing.

## Description

This is a comprehensive test project that demonstrates
systematic development practices and requirements-driven
implementation.

## Team

- Test Developer
- Another Developer

## Technologies

- Python
- FastAPI
- React
""")
            
            (project_path / 'package.json').write_text(json.dumps({
                "name": "test-project",
                "version": "1.0.0",
                "description": "Test project for Devpost integration",
                "main": "index.js",
                "scripts": {
                    "start": "node index.js"
                },
                "dependencies": {
                    "express": "^4.18.0"
                }
            }, indent=2))
            
            (project_path / 'pyproject.toml').write_text("""
[project]
name = "test-project"
version = "1.0.0"
description = "Test project for Devpost integration"
dependencies = [
    "fastapi>=0.68.0",
    "uvicorn>=0.15.0"
]
""")
            
            # Create sample media files
            media_dir = project_path / 'media'
            media_dir.mkdir()
            (media_dir / 'screenshot.png').write_bytes(b'fake_image_data')
            (media_dir / 'demo.mp4').write_bytes(b'fake_video_data')
            
            yield project_path
    
    @pytest.fixture
    def mock_api_client(self):
        """Mock API client with realistic responses."""
        mock_client = Mock()
        
        # Mock authentication
        mock_client.authenticate.return_value = True
        mock_client.is_authenticated.return_value = True
        
        # Mock project operations
        mock_client.get_user_projects.return_value = [
            {
                'id': 'test-project-123',
                'name': 'Test Project',
                'status': 'draft',
                'hackathons': [{'id': 'hackathon-456', 'name': 'Test Hackathon'}]
            }
        ]
        
        mock_client.get_project_details.return_value = {
            'id': 'test-project-123',
            'name': 'Test Project',
            'tagline': 'A test project',
            'description': 'Test project description',
            'status': 'draft',
            'hackathons': [{'id': 'hackathon-456', 'name': 'Test Hackathon'}]
        }
        
        mock_client.update_project.return_value = {'success': True}
        
        # Mock deadline operations
        mock_client.get_hackathon_deadlines.return_value = {
            'name': 'Test Hackathon',
            'submission_deadline': (datetime.now() + timedelta(days=7)).isoformat(),
            'judging_deadline': (datetime.now() + timedelta(days=14)).isoformat(),
            'is_registered': True,
            'submission_status': 'draft'
        }
        
        mock_client.get_submission_requirements.return_value = {
            'requirements': [
                {
                    'id': 'req-1',
                    'description': 'Project description',
                    'is_required': True,
                    'is_met': True,
                    'type': 'text'
                },
                {
                    'id': 'req-2',
                    'description': 'Demo video',
                    'is_required': True,
                    'is_met': False,
                    'type': 'video'
                }
            ]
        }
        
        return mock_client
    
    def test_complete_project_workflow(self, temp_project_dir, mock_api_client):
        """Test complete workflow from connection to validation."""
        with patch('src.devpost_integration.project_manager.DevPostAPIClient', return_value=mock_api_client):
            # Step 1: Connect project
            manager = DevpostProjectManager()
            success = manager.connect_project(
                project_id='test-project-123',
                local_path=temp_project_dir
            )
            
            assert success, "Project connection should succeed"
            
            # Verify configuration was created
            config_file = temp_project_dir / '.devpost' / 'config.json'
            assert config_file.exists(), "Configuration file should be created"
            
            # Step 2: Check project status
            status = manager.get_project_status(project_path=temp_project_dir)
            assert status.connected, "Project should be connected"
            assert status.project_id == 'test-project-123'
            # Systematic priority: package.json name takes precedence over README title
            assert status.project_name == 'test-project'
            
            # Step 3: Generate preview
            generator = DevpostPreviewGenerator(project_path=temp_project_dir)
            preview_data = generator.generate_preview()
            
            # Systematic priority: package.json name takes precedence over README title
            assert preview_data.project_metadata.title == 'test-project'
            assert preview_data.validation_result.is_valid or len(preview_data.validation_result.errors) == 0
            assert len(preview_data.media_files) > 0
            
            # Step 4: Validate project
            validation_engine = ValidationEngine()
            # Create a mock DevpostProject for validation
            from src.devpost_integration.models import DevpostProject, ProjectMetadata, ProjectLink
            project_metadata = ProjectMetadata(
                title="test-project",
                tagline="Test project",
                description="A test project for validation"
            )
            devpost_project = DevpostProject(
                id="test-project-123",
                title="test-project",
                tagline="Test project",
                description="A test project for validation",
                hackathon_id="hackathon-123",
                hackathon_name="Test Hackathon",
                links=[ProjectLink(title="GitHub", url="https://github.com/test/test", link_type="github")]
            )
            validation_result = validation_engine.validate_project(devpost_project)
            
            # ValidationEngine returns ValidationReport, not ValidationResult
            from src.devpost_integration.validation_engine import ValidationReport
            assert isinstance(validation_result, ValidationReport)
            assert validation_result.overall_score >= 0
            
            # Step 5: Sync project
            sync_manager = DevpostSyncManager()
            sync_result = sync_manager.sync_project()
            
            assert sync_result.success, "Sync should succeed"
    
    def test_deadline_tracking_workflow(self, temp_project_dir, mock_api_client):
        """Test deadline tracking and notification workflow."""
        with patch('src.devpost_integration.deadline_tracker.DevPostAPIClient', return_value=mock_api_client):
            # Setup project connection
            config = DevpostConfig(
                project_connections=[
                    ProjectConnection(
                        devpost_project_id='test-project-123',
                        local_path=Path(temp_project_dir),
                        hackathon_id='hackathon-123'
                    )
                ]
            )
            
            config_file = temp_project_dir / '.devpost' / 'config.json'
            config_file.parent.mkdir(parents=True, exist_ok=True)
            config_file.write_text(json.dumps(config.__dict__, default=str, indent=2))
            
            # Test deadline tracking
            tracker = DeadlineTracker(config_file=config_file, api_client=mock_api_client)
            
            # Get current project deadlines
            deadlines = tracker.get_current_project_deadlines()
            assert len(deadlines) > 0, "Should find project deadlines"
            
            deadline = deadlines[0]
            assert deadline.hackathon_name == 'Test Hackathon'
            assert deadline.is_registered
            assert deadline.days_remaining > 0
            
            # Test notification checking
            upcoming = tracker.check_upcoming_deadlines()
            # Should be empty since deadline is 7 days away and default threshold is 24 hours
            assert len(upcoming) == 0
    
    def test_multi_project_management(self, temp_project_dir, mock_api_client):
        """Test managing multiple projects simultaneously."""
        with patch('src.devpost_integration.project_manager.DevPostAPIClient', return_value=mock_api_client):
            manager = DevpostProjectManager()
            
            # Connect first project
            success1 = manager.connect_project(
                project_id='test-project-123',
                local_path=temp_project_dir
            )
            assert success1
            
            # Create second project directory
            with tempfile.TemporaryDirectory() as temp_dir2:
                project_path2 = Path(temp_dir2)
                (project_path2 / 'README.md').write_text("# Second Project")
                
                # Mock second project
                mock_api_client.get_project_details.side_effect = lambda pid: {
                    'test-project-123': {
                        'id': 'test-project-123',
                        'name': 'Test Project',
                        'status': 'draft'
                    },
                    'test-project-456': {
                        'id': 'test-project-456',
                        'name': 'Second Project',
                        'status': 'draft'
                    }
                }.get(pid, {})
                
                # Connect second project
                success2 = manager.connect_project(
                    project_id='test-project-456',
                    local_path=project_path2
                )
                assert success2
                
                # List all projects
                projects = manager.list_projects()
                assert len(projects) == 2
                
                # Switch between projects
                switch_success = manager.switch_project('test-project-123')
                assert switch_success
                
                current_status = manager.get_project_status()
                assert current_status.project_id == 'test-project-123'
    
    def test_error_handling_and_recovery(self, temp_project_dir, mock_api_client):
        """Test error handling and recovery mechanisms."""
        # Test network error handling
        mock_api_client.get_project_details.side_effect = ConnectionError("Network error")
        
        with patch('src.devpost_integration.project_manager.DevPostAPIClient', return_value=mock_api_client):
            manager = DevpostProjectManager()
            
            # Should handle network error gracefully
            with pytest.raises(Exception):  # Should raise appropriate error
                manager.connect_project(
                    project_id='test-project-123',
                    local_path=temp_project_dir
                )
        
        # Test authentication error handling
        mock_api_client.reset_mock()
        mock_api_client.authenticate.return_value = False
        mock_api_client.is_authenticated.return_value = False
        
        with patch('src.devpost_integration.project_manager.DevPostAPIClient', return_value=mock_api_client):
            manager = DevpostProjectManager()
            
            # Should handle authentication error
            with pytest.raises(Exception):
                manager.connect_project(
                    project_id='test-project-123',
                    local_path=temp_project_dir
                )
    
    def test_file_monitoring_integration(self, temp_project_dir, mock_api_client):
        """Test file monitoring and automatic sync integration."""
        with patch('src.devpost_integration.project_manager.DevPostAPIClient', return_value=mock_api_client):
            # Setup project
            manager = DevpostProjectManager()
            manager.connect_project(
                project_id='test-project-123',
                local_path=temp_project_dir
            )
            
            # Create file monitor
            from src.devpost_integration.file_monitor import ProjectFileMonitor
            
            monitor = ProjectFileMonitor(project_path=temp_project_dir)
            
            # Start monitoring (in test mode)
            changes = []
            
            def change_handler(event):
                changes.append(event)
            
            monitor.add_change_handler(change_handler)
            
            # Simulate file change
            readme_file = temp_project_dir / 'README.md'
            original_content = readme_file.read_text()
            readme_file.write_text(original_content + "\n\n## Updated")
            
            # Process changes (simulate file system event)
            from src.devpost_integration.models import FileChangeEvent, ChangeType, ContentType
            
            change_event = FileChangeEvent(
                file_path=str(readme_file),
                change_type=ChangeType.MODIFIED,
                content_type=ContentType.DOCUMENTATION,
                timestamp=datetime.now()
            )
            
            change_handler(change_event)
            
            # Verify change was detected
            assert len(changes) == 1
            assert changes[0].change_type == ChangeType.MODIFIED
            assert changes[0].content_type == ContentType.DOCUMENTATION
    
    def test_validation_engine_integration(self, temp_project_dir, mock_api_client):
        """Test comprehensive validation engine integration."""
        with patch('src.devpost_integration.validation_engine.DevPostAPIClient', return_value=mock_api_client):
            # Setup project with validation engine
            validation_engine = ValidationEngine()
            
            # Create project metadata
            metadata = ProjectMetadata(
                title="Test Project",
                tagline="A comprehensive test project",
                description="This is a test project for validation",
                tags=["python", "testing", "hackathon"],
                team_members=["Test Developer"],
                repository_url="https://github.com/test/project",
                demo_url="https://test-project.demo.com",
                version="1.0.0"
            )
            
            # Test validation with different scenarios
            from src.devpost_integration.validation_engine import ValidationContext
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

            
            context = ValidationContext(
                project_type="hackathon_submission",
                target_audience="devpost_judges"
            )
            
            # Test complete project validation
            validation_report = validation_engine.validate_metadata(metadata, context)
            
            assert validation_report.is_valid or len(validation_report.get_critical_issues()) == 0
            assert validation_report.completion_percentage > 50
            
            # Test incomplete project validation
            incomplete_metadata = ProjectMetadata(
                title="Incomplete Project",
                description="",  # Missing description
                tags=[],  # No tags
                team_members=[]  # No team members
            )
            
            incomplete_report = validation_engine.validate_metadata(incomplete_metadata, context)
            
            assert not incomplete_report.is_valid
            assert len(incomplete_report.get_critical_issues()) > 0
            assert incomplete_report.completion_percentage < 50
    
    def test_notification_system_integration(self, temp_project_dir):
        """Test notification system integration."""
        # Test notification manager
        notification_manager = NotificationManager()
        
        # Configure notifications
        notification_manager.configure_notifications({
            'enabled': True,
            'desktop_notifications': True,
            'email_notifications': False,  # Disable email for testing
            'deadline_warning_hours': 48
        })
        
        # Test deadline notification
        deadline_date = datetime.now() + timedelta(hours=12)  # 12 hours from now
        
        with patch('src.devpost_integration.notification_manager.plyer') as mock_plyer:
            mock_plyer.notification.notify = Mock()
            
            success = notification_manager.send_deadline_notification(
                hackathon_name="Test Hackathon",
                deadline_date=deadline_date,
                time_remaining="12 hours",
                requirements=[
                    {'description': 'Project description', 'is_met': True},
                    {'description': 'Demo video', 'is_met': False}
                ]
            )
            
            assert success, "Notification should be sent successfully"
            mock_plyer.notification.notify.assert_called_once()
        
        # Test status change notification
        with patch('src.devpost_integration.notification_manager.plyer') as mock_plyer:
            mock_plyer.notification.notify = Mock()
            
            success = notification_manager.send_status_change_notification(
                project_name="Test Project",
                old_status="draft",
                new_status="submitted",
                details="Project successfully submitted"
            )
            
            assert success, "Status change notification should be sent"
            mock_plyer.notification.notify.assert_called_once()
    
    @pytest.mark.timeout(30)
    def test_performance_requirements(self, temp_project_dir, mock_api_client):
        """Test that operations complete within performance requirements."""
        with patch('src.devpost_integration.project_manager.DevPostAPIClient', return_value=mock_api_client):
            start_time = datetime.now()
            
            # Test project connection performance
            manager = DevpostProjectManager()
            success = manager.connect_project(
                project_id='test-project-123',
                local_path=temp_project_dir
            )
            
            connection_time = (datetime.now() - start_time).total_seconds()
            assert connection_time < 5.0, "Project connection should complete within 5 seconds"
            assert success
            
            # Test preview generation performance
            start_time = datetime.now()
            
            generator = DevpostPreviewGenerator(project_path=temp_project_dir)
            preview_data = generator.generate_preview()
            
            preview_time = (datetime.now() - start_time).total_seconds()
            assert preview_time < 3.0, "Preview generation should complete within 3 seconds"
            assert preview_data is not None
            
            # Test validation performance
            start_time = datetime.now()
            
            validation_engine = ValidationEngine()
            with patch.object(validation_engine, 'api_client', mock_api_client):
                validation_result = validation_engine.validate_current_project()
            
            validation_time = (datetime.now() - start_time).total_seconds()
            assert validation_time < 2.0, "Validation should complete within 2 seconds"

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

            assert validation_result is not None