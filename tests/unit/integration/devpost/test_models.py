"""
Unit tests for Devpost integration data models.

This module tests all data models including validation, serialization,
and deserialization functionality.
"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
from pydantic import ValidationError

from src.beast_mode.integration.devpost.models import (
    DevpostProject,
    ProjectMetadata,
    SyncOperation,
    FileChangeEvent,
    DevpostConfig,
    ProjectConnection,
    SubmissionStatus,
    ChangeType,
    SyncOperationType,
    SyncStatus,
    TeamMember,
    ProjectLink,
    MediaFile,
    AuthToken,
    AuthResult,
    SyncResult,
    ValidationResult,
    PreviewResult
)


class TestDevpostProject:
    """Test DevpostProject model."""
    
    def test_valid_project_creation(self):
        """Test creating a valid DevpostProject."""
        project = DevpostProject(
            id="test-123",
            title="Test Project",
            tagline="A test project",
            description="This is a test project for validation",
            hackathon_id="hack-456",
            hackathon_name="Test Hackathon"
        )
        
        assert project.id == "test-123"
        assert project.title == "Test Project"
        assert project.submission_status == SubmissionStatus.DRAFT
        assert isinstance(project.created_at, datetime)
    
    def test_title_validation(self):
        """Test title validation."""
        # Empty title should fail
        with pytest.raises(ValidationError, match="Project title cannot be empty"):
            DevpostProject(
                id="test-123",
                title="",
                tagline="A test project",
                description="Test description",
                hackathon_id="hack-456",
                hackathon_name="Test Hackathon"
            )
        
        # Whitespace-only title should fail
        with pytest.raises(ValidationError, match="Project title cannot be empty"):
            DevpostProject(
                id="test-123",
                title="   ",
                tagline="A test project",
                description="Test description",
                hackathon_id="hack-456",
                hackathon_name="Test Hackathon"
            )
    
    def test_tagline_validation(self):
        """Test tagline length validation."""
        long_tagline = "x" * 121
        
        with pytest.raises(ValidationError, match="Tagline must be 120 characters or less"):
            DevpostProject(
                id="test-123",
                title="Test Project",
                tagline=long_tagline,
                description="Test description",
                hackathon_id="hack-456",
                hackathon_name="Test Hackathon"
            )
    
    def test_description_validation(self):
        """Test description length validation."""
        long_description = "x" * 5001
        
        with pytest.raises(ValidationError, match="Description must be 5000 characters or less"):
            DevpostProject(
                id="test-123",
                title="Test Project",
                tagline="Test tagline",
                description=long_description,
                hackathon_id="hack-456",
                hackathon_name="Test Hackathon"
            )
    
    def test_tags_validation(self):
        """Test tags validation."""
        # Too many tags
        many_tags = [f"tag{i}" for i in range(11)]
        
        with pytest.raises(ValidationError, match="Maximum 10 tags allowed"):
            DevpostProject(
                id="test-123",
                title="Test Project",
                tagline="Test tagline",
                description="Test description",
                hackathon_id="hack-456",
                hackathon_name="Test Hackathon",
                tags=many_tags
            )
        
        # Invalid tag characters
        with pytest.raises(ValidationError, match="Tags can only contain"):
            DevpostProject(
                id="test-123",
                title="Test Project",
                tagline="Test tagline",
                description="Test description",
                hackathon_id="hack-456",
                hackathon_name="Test Hackathon",
                tags=["valid-tag", "invalid@tag"]
            )
    
    def test_deadline_validation(self):
        """Test deadline validation."""
        past_deadline = datetime.now() - timedelta(days=1)
        
        with pytest.raises(ValidationError, match="Deadline must be in the future"):
            DevpostProject(
                id="test-123",
                title="Test Project",
                tagline="Test tagline",
                description="Test description",
                hackathon_id="hack-456",
                hackathon_name="Test Hackathon",
                deadline=past_deadline
            )
    
    def test_serialization(self):
        """Test project serialization."""
        project = DevpostProject(
            id="test-123",
            title="Test Project",
            tagline="A test project",
            description="This is a test project",
            hackathon_id="hack-456",
            hackathon_name="Test Hackathon"
        )
        
        # Test to_dict
        project_dict = project.to_dict()
        assert isinstance(project_dict, dict)
        assert project_dict["id"] == "test-123"
        assert project_dict["title"] == "Test Project"
        
        # Test to_json
        project_json = project.to_json()
        assert isinstance(project_json, str)
        parsed = json.loads(project_json)
        assert parsed["id"] == "test-123"
        
        # Test from_dict
        recreated = DevpostProject.from_dict(project_dict)
        assert recreated.id == project.id
        assert recreated.title == project.title
        
        # Test from_json
        recreated_json = DevpostProject.from_json(project_json)
        assert recreated_json.id == project.id
        assert recreated_json.title == project.title


class TestProjectMetadata:
    """Test ProjectMetadata model."""
    
    def test_valid_metadata_creation(self):
        """Test creating valid ProjectMetadata."""
        metadata = ProjectMetadata(
            title="Test Project",
            tagline="Test tagline",
            description="Test description",
            tags=["python", "ai"],
            team_members=["Alice", "Bob"]
        )
        
        assert metadata.title == "Test Project"
        assert len(metadata.tags) == 2
        assert len(metadata.team_members) == 2
    
    def test_title_validation(self):
        """Test title validation."""
        # Empty title
        with pytest.raises(ValidationError, match="Project title cannot be empty"):
            ProjectMetadata(title="")
        
        # Too long title
        long_title = "x" * 201
        with pytest.raises(ValidationError, match="Title must be 200 characters or less"):
            ProjectMetadata(title=long_title)
    
    def test_url_validation(self):
        """Test URL validation."""
        # Invalid URL
        with pytest.raises(ValidationError, match="URLs must start with http"):
            ProjectMetadata(
                title="Test",
                repository_url="invalid-url"
            )
        
        # Valid URLs
        metadata = ProjectMetadata(
            title="Test",
            repository_url="https://github.com/user/repo",
            demo_url="http://demo.com",
            video_url="https://youtube.com/watch?v=123"
        )
        
        assert metadata.repository_url == "https://github.com/user/repo"
        assert metadata.demo_url == "http://demo.com"
        assert metadata.video_url == "https://youtube.com/watch?v=123"
    
    def test_team_members_validation(self):
        """Test team members validation."""
        # Too many team members
        many_members = [f"Member {i}" for i in range(21)]
        
        with pytest.raises(ValidationError, match="Maximum 20 team members allowed"):
            ProjectMetadata(
                title="Test",
                team_members=many_members
            )
        
        # Too long member name
        long_name = "x" * 101
        with pytest.raises(ValidationError, match="Team member name must be 100 characters or less"):
            ProjectMetadata(
                title="Test",
                team_members=[long_name]
            )
    
    def test_completeness_validation(self):
        """Test completeness validation."""
        # Incomplete metadata
        metadata = ProjectMetadata(title="Test")
        missing = metadata.validate_completeness()
        
        assert "description (minimum 50 characters)" in missing
        assert "tags" in missing
        assert "repository_url or demo_url" in missing
        
        # Complete metadata
        complete_metadata = ProjectMetadata(
            title="Test Project",
            description="x" * 60,  # More than 50 characters
            tags=["python"],
            repository_url="https://github.com/user/repo"
        )
        
        missing = complete_metadata.validate_completeness()
        assert len(missing) == 0
    
    def test_serialization(self):
        """Test metadata serialization."""
        metadata = ProjectMetadata(
            title="Test Project",
            description="Test description",
            tags=["python", "ai"]
        )
        
        # Test serialization methods
        metadata_dict = metadata.to_dict()
        assert isinstance(metadata_dict, dict)
        
        metadata_json = metadata.to_json()
        assert isinstance(metadata_json, str)
        
        # Test deserialization
        recreated = ProjectMetadata.from_dict(metadata_dict)
        assert recreated.title == metadata.title
        
        recreated_json = ProjectMetadata.from_json(metadata_json)
        assert recreated_json.title == metadata.title


class TestSyncOperation:
    """Test SyncOperation model."""
    
    def test_valid_sync_operation(self):
        """Test creating valid SyncOperation."""
        operation = SyncOperation(
            operation_type=SyncOperationType.METADATA_UPDATE,
            target_field="title",
            local_value="New Title",
            remote_value="Old Title",
            priority=3
        )
        
        assert operation.operation_type == SyncOperationType.METADATA_UPDATE
        assert operation.target_field == "title"
        assert operation.priority == 3
        assert operation.retry_count == 0
    
    def test_priority_validation(self):
        """Test priority validation."""
        # Invalid priority (too low)
        with pytest.raises(ValidationError, match="Priority must be between 1 and 10"):
            SyncOperation(
                operation_type=SyncOperationType.METADATA_UPDATE,
                target_field="title",
                local_value="New Title",
                priority=0
            )
        
        # Invalid priority (too high)
        with pytest.raises(ValidationError, match="Priority must be between 1 and 10"):
            SyncOperation(
                operation_type=SyncOperationType.METADATA_UPDATE,
                target_field="title",
                local_value="New Title",
                priority=11
            )
    
    def test_retry_validation(self):
        """Test retry count validation."""
        # Retry count exceeds max retries
        with pytest.raises(ValidationError, match="Retry count cannot exceed max retries"):
            SyncOperation(
                operation_type=SyncOperationType.METADATA_UPDATE,
                target_field="title",
                local_value="New Title",
                retry_count=5,
                max_retries=3
            )
    
    def test_retry_methods(self):
        """Test retry-related methods."""
        operation = SyncOperation(
            operation_type=SyncOperationType.METADATA_UPDATE,
            target_field="title",
            local_value="New Title",
            max_retries=2
        )
        
        # Can retry initially
        assert operation.can_retry() is True
        
        # Increment retry
        operation.increment_retry()
        assert operation.retry_count == 1
        assert operation.can_retry() is True
        
        # Increment again
        operation.increment_retry()
        assert operation.retry_count == 2
        assert operation.can_retry() is False
    
    def test_serialization(self):
        """Test sync operation serialization."""
        operation = SyncOperation(
            operation_type=SyncOperationType.METADATA_UPDATE,
            target_field="title",
            local_value="New Title"
        )
        
        # Test serialization methods
        op_dict = operation.to_dict()
        assert isinstance(op_dict, dict)
        
        op_json = operation.to_json()
        assert isinstance(op_json, str)
        
        # Test deserialization
        recreated = SyncOperation.from_dict(op_dict)
        assert recreated.operation_type == operation.operation_type
        
        recreated_json = SyncOperation.from_json(op_json)
        assert recreated_json.operation_type == operation.operation_type


class TestFileChangeEvent:
    """Test FileChangeEvent model."""
    
    def test_valid_file_change_event(self):
        """Test creating valid FileChangeEvent."""
        event = FileChangeEvent(
            file_path=Path("README.md"),
            change_type=ChangeType.MODIFIED,
            file_size=1024
        )
        
        assert event.file_path == Path("README.md")
        assert event.change_type == ChangeType.MODIFIED
        assert event.file_size == 1024
        assert isinstance(event.timestamp, datetime)
    
    def test_file_size_validation(self):
        """Test file size validation."""
        # Negative file size
        with pytest.raises(ValidationError, match="File size cannot be negative"):
            FileChangeEvent(
                file_path=Path("test.txt"),
                change_type=ChangeType.CREATED,
                file_size=-1
            )
    
    def test_deleted_file_validation(self):
        """Test deleted file validation."""
        # Deleted file should not have file size
        with pytest.raises(ValidationError, match="Deleted files should not have file size"):
            FileChangeEvent(
                file_path=Path("test.txt"),
                change_type=ChangeType.DELETED,
                file_size=1024
            )
    
    def test_file_type_detection(self):
        """Test file type detection methods."""
        # Media file
        media_event = FileChangeEvent(
            file_path=Path("screenshot.png"),
            change_type=ChangeType.CREATED
        )
        assert media_event.is_media_file() is True
        assert media_event.is_documentation_file() is False
        
        # Documentation file
        doc_event = FileChangeEvent(
            file_path=Path("README.md"),
            change_type=ChangeType.MODIFIED
        )
        assert doc_event.is_media_file() is False
        assert doc_event.is_documentation_file() is True
        
        # Regular file
        regular_event = FileChangeEvent(
            file_path=Path("main.py"),
            change_type=ChangeType.CREATED
        )
        assert regular_event.is_media_file() is False
        assert regular_event.is_documentation_file() is False
    
    def test_sync_trigger_detection(self):
        """Test sync trigger detection."""
        event = FileChangeEvent(
            file_path=Path("README.md"),
            change_type=ChangeType.MODIFIED
        )
        
        watch_patterns = ["README*", "*.md", "package.json"]
        
        assert event.should_trigger_sync(watch_patterns) is True
        
        # File that doesn't match patterns
        code_event = FileChangeEvent(
            file_path=Path("main.py"),
            change_type=ChangeType.MODIFIED
        )
        
        assert code_event.should_trigger_sync(watch_patterns) is False
    
    def test_serialization(self):
        """Test file change event serialization."""
        event = FileChangeEvent(
            file_path=Path("README.md"),
            change_type=ChangeType.MODIFIED
        )
        
        # Test serialization methods
        event_dict = event.to_dict()
        assert isinstance(event_dict, dict)
        
        event_json = event.to_json()
        assert isinstance(event_json, str)
        
        # Test deserialization
        recreated = FileChangeEvent.from_dict(event_dict)
        assert recreated.file_path == event.file_path
        
        recreated_json = FileChangeEvent.from_json(event_json)
        assert recreated_json.file_path == event.file_path


class TestDevpostConfig:
    """Test DevpostConfig model."""
    
    def test_valid_config_creation(self):
        """Test creating valid DevpostConfig."""
        config = DevpostConfig(
            project_id="proj-123",
            hackathon_id="hack-456"
        )
        
        assert config.project_id == "proj-123"
        assert config.hackathon_id == "hack-456"
        assert config.sync_enabled is True
        assert config.sync_interval == 300
    
    def test_sync_interval_validation(self):
        """Test sync interval validation."""
        # Too small interval
        with pytest.raises(ValidationError, match="Sync interval must be at least 60 seconds"):
            DevpostConfig(
                project_id="proj-123",
                hackathon_id="hack-456",
                sync_interval=30
            )
        
        # Negative interval
        with pytest.raises(ValidationError, match="Sync interval must be positive"):
            DevpostConfig(
                project_id="proj-123",
                hackathon_id="hack-456",
                sync_interval=-1
            )
    
    def test_watch_patterns_validation(self):
        """Test watch patterns validation."""
        # Empty patterns list
        with pytest.raises(ValidationError, match="At least one watch pattern is required"):
            DevpostConfig(
                project_id="proj-123",
                hackathon_id="hack-456",
                watch_patterns=[]
            )
        
        # Empty pattern string
        with pytest.raises(ValidationError, match="Watch patterns cannot be empty"):
            DevpostConfig(
                project_id="proj-123",
                hackathon_id="hack-456",
                watch_patterns=["README*", ""]
            )
    
    def test_configuration_validation(self):
        """Test configuration completeness validation."""
        # Missing project_id
        config = DevpostConfig(
            project_id="",
            hackathon_id="hack-456"
        )
        issues = config.validate_configuration()
        assert "project_id is required" in issues
        
        # Missing hackathon_id
        config = DevpostConfig(
            project_id="proj-123",
            hackathon_id=""
        )
        issues = config.validate_configuration()
        assert "hackathon_id is required" in issues
        
        # This test is handled by the watch_patterns validation test above
        
        # Valid configuration
        config = DevpostConfig(
            project_id="proj-123",
            hackathon_id="hack-456"
        )
        issues = config.validate_configuration()
        assert len(issues) == 0
    
    def test_serialization(self):
        """Test config serialization."""
        config = DevpostConfig(
            project_id="proj-123",
            hackathon_id="hack-456"
        )
        
        # Test serialization methods
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        
        config_json = config.to_json()
        assert isinstance(config_json, str)
        
        # Test deserialization
        recreated = DevpostConfig.from_dict(config_dict)
        assert recreated.project_id == config.project_id
        
        recreated_json = DevpostConfig.from_json(config_json)
        assert recreated_json.project_id == config.project_id


@pytest.mark.integration
class TestModelIntegration:
    """Integration tests for model interactions."""
    
    def test_project_metadata_to_devpost_project(self):
        """Test converting ProjectMetadata to DevpostProject data."""
        metadata = ProjectMetadata(
            title="Test Project",
            tagline="Test tagline",
            description="Test description for the project",
            tags=["python", "ai"],
            team_members=["Alice", "Bob"],
            repository_url="https://github.com/user/repo"
        )
        
        # Convert to dict for DevpostProject creation
        metadata_dict = metadata.to_dict()
        
        # Create DevpostProject with metadata (convert team members to TeamMember objects)
        team_members = [TeamMember(username=name, display_name=name) for name in metadata.team_members]
        
        project = DevpostProject(
            id="proj-123",
            hackathon_id="hack-456",
            hackathon_name="Test Hackathon",
            title=metadata.title,
            tagline=metadata.tagline,
            description=metadata.description,
            tags=metadata.tags,
            team_members=team_members
        )
        
        assert project.title == metadata.title
        assert project.tagline == metadata.tagline
        assert project.description == metadata.description
        assert project.tags == metadata.tags
    
    def test_sync_operation_workflow(self):
        """Test sync operation workflow."""
        # Create sync operation
        operation = SyncOperation(
            operation_type=SyncOperationType.METADATA_UPDATE,
            target_field="title",
            local_value="New Title",
            remote_value="Old Title"
        )
        
        # Simulate failure and retry
        assert operation.can_retry() is True
        operation.increment_retry()
        operation.error_message = "Network timeout"
        
        # Serialize for persistence
        op_json = operation.to_json()
        
        # Deserialize and continue
        restored_op = SyncOperation.from_json(op_json)
        assert restored_op.retry_count == 1
        assert restored_op.error_message == "Network timeout"
        assert restored_op.can_retry() is True
    
    def test_file_change_to_sync_operation(self):
        """Test converting file changes to sync operations."""
        # Documentation file change
        doc_change = FileChangeEvent(
            file_path=Path("README.md"),
            change_type=ChangeType.MODIFIED
        )
        
        if doc_change.is_documentation_file():
            sync_op = SyncOperation(
                operation_type=SyncOperationType.DOCUMENTATION_UPDATE,
                target_field="description",
                local_value="Updated README content",
                priority=2  # High priority for documentation
            )
            
            assert sync_op.operation_type == SyncOperationType.DOCUMENTATION_UPDATE
            assert sync_op.priority == 2
        
        # Media file change
        media_change = FileChangeEvent(
            file_path=Path("screenshot.png"),
            change_type=ChangeType.CREATED,
            file_size=2048
        )
        
        if media_change.is_media_file():
            sync_op = SyncOperation(
                operation_type=SyncOperationType.MEDIA_UPLOAD,
                target_field="media",
                local_value=str(media_change.file_path),
                priority=3  # Medium priority for media
            )
            
            assert sync_op.operation_type == SyncOperationType.MEDIA_UPLOAD
            assert sync_op.priority == 3