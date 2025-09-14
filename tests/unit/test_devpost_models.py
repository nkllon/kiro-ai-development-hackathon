#!/usr/bin/env python3
"""
Unit tests for Devpost Integration Data Models

Testing the Requirements ARE the Solution - Data Model Validation
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from src.devpost_integration.models import (
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    # Core Models
    DevpostProject, ProjectMetadata, TeamMember, ProjectLink, MediaFile,
    SubmissionRequirement, SyncOperation, FileChangeEvent,
    
    # Deadline and Notification Models (Task 2.3)
    Deadline, ProjectSummary, NotificationSettings, ValidationRules,
    NotificationMessage, ReminderTiming, GlobalSettings,
    
    # Configuration Models
    DevpostConfig, ProjectConnection, MultiProjectConfig,
    
    # Result Models
    SyncResult, ValidationResult, PreviewData, ProjectStatus,
    AuthResult, ConnectionResult, ContextSwitchResult, ConflictResolution,
    ProjectDashboard, FormattingIssue, CompletionStatus,
    
    # Enums
    SubmissionStatus, ChangeType, ContentType, SyncOperationType,
    DeadlineType, MediaType, NotificationTiming, ConflictResolutionStrategy,
    
    # Utility Functions
    validate_project_metadata, create_default_notification_settings,
    create_default_validation_rules
)


class TestCoreModels(ReflectiveModule):
    """Test core data models."""
    
    def test_devpost_project_creation(self):
        """Test DevpostProject model creation and defaults."""
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
        assert len(project.team_members) == 0
        assert len(project.tags) == 0
        assert len(project.links) == 0
        assert len(project.media) == 0
    
    def test_project_metadata_validation(self):
        """Test project metadata validation."""
        # Valid metadata
        metadata = ProjectMetadata(
            title="Valid Project Title",
            tagline="This is a valid tagline with enough characters",
            description="This is a comprehensive description that meets the minimum length requirement of 100 characters. It provides detailed information about the project and its goals.",
            tags=["python", "ai", "hackathon"],
            team_members=["Alice", "Bob"]
        )
        
        result = validate_project_metadata(metadata)
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.completion_percentage == 100.0
    
    def test_project_metadata_validation_failures(self):
        """Test project metadata validation with invalid data."""
        # Invalid metadata - too short
        metadata = ProjectMetadata(
            title="Hi",  # Too short
            tagline="Short",  # Too short
            description="Short desc",  # Too short
            tags=[],  # Empty
            team_members=[]  # Empty
        )
        
        result = validate_project_metadata(metadata)
        assert not result.is_valid
        assert len(result.errors) == 3  # title, tagline, description
        assert len(result.warnings) == 2  # tags, team_members
        assert "title" in result.missing_fields
        assert "tagline" in result.missing_fields
        assert "description" in result.missing_fields
        assert result.completion_percentage < 100.0
    
    def test_team_member_model(self):
        """Test TeamMember model."""
        member = TeamMember(
            name="Alice Smith",
            email="alice@example.com",
            role="Developer",
            devpost_username="alice_dev"
        )
        
        assert member.name == "Alice Smith"
        assert member.email == "alice@example.com"
        assert member.role == "Developer"
        assert member.devpost_username == "alice_dev"
    
    def test_media_file_model(self):
        """Test MediaFile model."""
        media = MediaFile(
            filename="screenshot.png",
            file_path=Path("images/screenshot.png"),
            media_type=MediaType.SCREENSHOT,
            caption="Main application screenshot",
            file_size=1024000
        )
        
        assert media.filename == "screenshot.png"
        assert media.media_type == MediaType.SCREENSHOT
        assert media.caption == "Main application screenshot"
        assert media.file_size == 1024000
        assert media.upload_url is None
        assert media.uploaded_at is None


class TestDeadlineAndNotificationModels(ReflectiveModule):
    """Test deadline and notification models (Task 2.3)."""
    
    def test_deadline_creation(self):
        """Test Deadline model creation and methods."""
        future_time = datetime.now() + timedelta(days=7)
        deadline = Deadline(
            hackathon_id="hack-123",
            project_id="proj-456",
            deadline_type=DeadlineType.SUBMISSION,
            deadline_time=future_time,
            description="Final submission deadline",
            is_hard_deadline=True
        )
        
        assert deadline.hackathon_id == "hack-123"
        assert deadline.project_id == "proj-456"
        assert deadline.deadline_type == DeadlineType.SUBMISSION
        assert deadline.deadline_time == future_time
        assert deadline.is_hard_deadline
        assert len(deadline.requirements) == 0
        assert len(deadline.notification_schedule) == 0
    
    def test_deadline_time_calculations(self):
        """Test deadline time calculation methods."""
        # Future deadline
        future_time = datetime.now() + timedelta(days=3, hours=2)
        deadline = Deadline(
            hackathon_id="hack-123",
            project_id="proj-456",
            deadline_type=DeadlineType.SUBMISSION,
            deadline_time=future_time
        )
        
        time_remaining = deadline.time_remaining()
        assert time_remaining.days >= 2  # Should be around 3 days
        assert deadline.is_approaching(timedelta(days=5))  # Within 5 days
        assert not deadline.is_approaching(timedelta(days=1))  # Not within 1 day
        assert not deadline.is_overdue()
        
        # Past deadline
        past_time = datetime.now() - timedelta(hours=1)
        past_deadline = Deadline(
            hackathon_id="hack-123",
            project_id="proj-456",
            deadline_type=DeadlineType.SUBMISSION,
            deadline_time=past_time
        )
        
        assert past_deadline.is_overdue()
        assert past_deadline.time_remaining().total_seconds() < 0
    
    def test_project_summary_model(self):
        """Test ProjectSummary model for multi-project management."""
        summary = ProjectSummary(
            project_id="proj-123",
            title="Test Project",
            hackathon_name="Test Hackathon",
            deadline=datetime.now() + timedelta(days=5),
            submission_status=SubmissionStatus.DRAFT,
            completion_percentage=75.5,
            last_sync=datetime.now() - timedelta(hours=2),
            pending_changes=3,
            validation_errors=1,
            is_active=True
        )
        
        assert summary.project_id == "proj-123"
        assert summary.title == "Test Project"
        assert summary.completion_percentage == 75.5
        assert summary.pending_changes == 3
        assert summary.validation_errors == 1
        assert summary.is_active
    
    def test_notification_settings_model(self):
        """Test NotificationSettings model."""
        settings = NotificationSettings(
            desktop_notifications=True,
            email_notifications=False,
            deadline_advance_times=[
                timedelta(days=7),
                timedelta(days=1),
                timedelta(hours=1)
            ],
            sync_failure_notifications=True,
            submission_status_notifications=True,
            quiet_hours_start=22,
            quiet_hours_end=8
        )
        
        assert settings.desktop_notifications
        assert not settings.email_notifications
        assert len(settings.deadline_advance_times) == 3
        assert settings.quiet_hours_start == 22
        assert settings.quiet_hours_end == 8
    
    def test_validation_rules_model(self):
        """Test ValidationRules model."""
        rules = ValidationRules(
            required_fields=["title", "tagline", "description", "demo_url"],
            min_description_length=150,
            required_media_types=[MediaType.SCREENSHOT, MediaType.VIDEO],
            team_member_validation=True,
            link_validation=True,
            max_tags=8,
            custom_rules={"min_team_size": 2, "max_team_size": 4}
        )
        
        assert len(rules.required_fields) == 4
        assert rules.min_description_length == 150
        assert MediaType.SCREENSHOT in rules.required_media_types
        assert MediaType.VIDEO in rules.required_media_types
        assert rules.max_tags == 8
        assert rules.custom_rules["min_team_size"] == 2
    
    def test_notification_message_model(self):
        """Test NotificationMessage model."""
        message = NotificationMessage(
            title="Deadline Approaching",
            message="Your hackathon submission deadline is in 24 hours!",
            project_id="proj-123",
            notification_type="deadline",
            action_url="https://devpost.com/projects/proj-123"
        )
        
        assert message.title == "Deadline Approaching"
        assert message.notification_type == "deadline"
        assert message.project_id == "proj-123"
        assert not message.delivered
        assert message.action_url is not None
    
    def test_reminder_timing_model(self):
        """Test ReminderTiming model."""
        reminder = ReminderTiming(
            advance_time=timedelta(days=3),
            notification_type="deadline_reminder",
            enabled=True,
            custom_message="Don't forget to submit your project!"
        )
        
        assert reminder.advance_time == timedelta(days=3)
        assert reminder.notification_type == "deadline_reminder"
        assert reminder.enabled
        assert reminder.custom_message is not None
    
    def test_global_settings_model(self):
        """Test GlobalSettings model."""
        settings = GlobalSettings(
            default_sync_interval=600,
            max_concurrent_projects=5,
            auto_switch_on_file_change=True,
            unified_notifications=False,
            backup_configurations=True,
            analytics_enabled=False
        )
        
        assert settings.default_sync_interval == 600
        assert settings.max_concurrent_projects == 5
        assert settings.auto_switch_on_file_change
        assert not settings.unified_notifications
        assert settings.backup_configurations
        assert not settings.analytics_enabled


class TestConfigurationModels(ReflectiveModule):
    """Test configuration models."""
    
    def test_devpost_config_creation(self):
        """Test DevpostConfig model creation with defaults."""
        config = DevpostConfig(
            project_id="proj-123",
            hackathon_id="hack-456"
        )
        
        assert config.project_id == "proj-123"
        assert config.hackathon_id == "hack-456"
        assert config.sync_enabled
        assert config.sync_interval == 300
        assert config.auto_sync_media
        assert len(config.watch_patterns) > 0
        assert "*.md" in config.watch_patterns
        assert "*.py" in config.watch_patterns
        assert isinstance(config.notification_preferences, NotificationSettings)
        assert isinstance(config.validation_rules, ValidationRules)
    
    def test_project_connection_model(self):
        """Test ProjectConnection model."""
        connection = ProjectConnection(
            local_path=Path("/path/to/project"),
            devpost_project_id="proj-123",
            hackathon_id="hack-456",
            last_sync=datetime.now() - timedelta(hours=1),
            sync_status="synced",
            is_active=True
        )
        
        assert connection.local_path == Path("/path/to/project")
        assert connection.devpost_project_id == "proj-123"
        assert connection.hackathon_id == "hack-456"
        assert connection.sync_status == "synced"
        assert connection.is_active
        assert isinstance(connection.configuration, DevpostConfig)
    
    def test_multi_project_config_model(self):
        """Test MultiProjectConfig model."""
        config = MultiProjectConfig(
            active_project_id="proj-123",
            conflict_resolution_strategy=ConflictResolutionStrategy.TIMESTAMP_BASED
        )
        
        assert config.active_project_id == "proj-123"
        assert config.conflict_resolution_strategy == ConflictResolutionStrategy.TIMESTAMP_BASED
        assert len(config.project_connections) == 0
        assert len(config.global_settings) == 0


class TestResultModels(ReflectiveModule):
    """Test result and status models."""
    
    def test_sync_result_model(self):
        """Test SyncResult model."""
        result = SyncResult(
            success=True,
            changes_made=["Updated description", "Added screenshot"],
            sync_duration=timedelta(seconds=15)
        )
        
        assert result.success
        assert len(result.changes_made) == 2
        assert result.error is None
        assert result.sync_duration == timedelta(seconds=15)
        assert isinstance(result.timestamp, datetime)
    
    def test_validation_result_model(self):
        """Test ValidationResult model."""
        result = ValidationResult(
            is_valid=False,
            errors=["Title too short", "Missing description"],
            warnings=["No tags specified"],
            missing_fields=["title", "description"],
            completion_percentage=60.0
        )
        
        assert not result.is_valid
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
        assert len(result.missing_fields) == 2
        assert result.completion_percentage == 60.0
    
    def test_project_status_model(self):
        """Test ProjectStatus model."""
        status = ProjectStatus(
            connected=True,
            project_id="proj-123",
            project_name="Test Project",
            local_path=Path("/path/to/project"),
            last_sync=datetime.now() - timedelta(minutes=30),
            pending_changes=["README.md updated", "Added image"],
            validation_errors=["Missing tagline"],
            deadline=datetime.now() + timedelta(days=2)
        )
        
        assert status.connected
        assert status.project_id == "proj-123"
        assert status.project_name == "Test Project"
        assert len(status.pending_changes) == 2
        assert len(status.validation_errors) == 1
        assert status.deadline is not None
    
    def test_project_dashboard_model(self):
        """Test ProjectDashboard model."""
        project1 = ProjectSummary(
            project_id="proj-1",
            title="Project 1",
            hackathon_name="Hackathon A",
            deadline=datetime.now() + timedelta(days=5)
        )
        
        project2 = ProjectSummary(
            project_id="proj-2",
            title="Project 2",
            hackathon_name="Hackathon B",
            deadline=datetime.now() - timedelta(days=1)  # Overdue
        )
        
        dashboard = ProjectDashboard(
            projects=[project1, project2],
            active_project=project1,
            total_projects=2,
            projects_with_deadlines=2,
            overdue_projects=1
        )
        
        assert len(dashboard.projects) == 2
        assert dashboard.active_project == project1
        assert dashboard.total_projects == 2
        assert dashboard.projects_with_deadlines == 2
        assert dashboard.overdue_projects == 1
        assert isinstance(dashboard.generated_at, datetime)


class TestUtilityFunctions(ReflectiveModule):
    """Test utility functions."""
    
    def test_create_default_notification_settings(self):
        """Test default notification settings creation."""
        settings = create_default_notification_settings()
        
        assert isinstance(settings, NotificationSettings)
        assert settings.desktop_notifications
        assert not settings.email_notifications
        assert len(settings.deadline_advance_times) == 5
        assert timedelta(days=7) in settings.deadline_advance_times
        assert timedelta(hours=1) in settings.deadline_advance_times
        assert settings.sync_failure_notifications
        assert settings.submission_status_notifications
    
    def test_create_default_validation_rules(self):
        """Test default validation rules creation."""
        rules = create_default_validation_rules()
        
        assert isinstance(rules, ValidationRules)
        assert "title" in rules.required_fields
        assert "tagline" in rules.required_fields
        assert "description" in rules.required_fields
        assert rules.min_description_length == 100
        assert rules.team_member_validation
        assert rules.link_validation
        assert rules.max_tags == 10


class TestEnums(ReflectiveModule):
    """Test enum values and behavior."""
    
    def test_submission_status_enum(self):
        """Test SubmissionStatus enum."""
        assert SubmissionStatus.DRAFT == "draft"
        assert SubmissionStatus.SUBMITTED == "submitted"
        assert SubmissionStatus.JUDGING == "judging"
        assert SubmissionStatus.COMPLETE == "complete"
        assert SubmissionStatus.WITHDRAWN == "withdrawn"
    
    def test_deadline_type_enum(self):
        """Test DeadlineType enum."""
        assert DeadlineType.SUBMISSION == "submission"
        assert DeadlineType.JUDGING == "judging"
        assert DeadlineType.FINAL == "final"
        assert DeadlineType.MILESTONE == "milestone"
    
    def test_notification_timing_enum(self):
        """Test NotificationTiming enum."""
        assert NotificationTiming.SEVEN_DAYS == "7_days"
        assert NotificationTiming.THREE_DAYS == "3_days"
        assert NotificationTiming.ONE_DAY == "1_day"
        assert NotificationTiming.SIX_HOURS == "6_hours"
        assert NotificationTiming.ONE_HOUR == "1_hour"
        assert NotificationTiming.THIRTY_MINUTES == "30_minutes"
    
    def test_conflict_resolution_strategy_enum(self):
        """Test ConflictResolutionStrategy enum."""
        assert ConflictResolutionStrategy.LOCAL_WINS == "local_wins"
        assert ConflictResolutionStrategy.REMOTE_WINS == "remote_wins"
        assert ConflictResolutionStrategy.MANUAL_RESOLUTION == "manual_resolution"
        assert ConflictResolutionStrategy.TIMESTAMP_BASED == "timestamp_based"


class TestModelIntegration(ReflectiveModule):
    """Test model integration and relationships."""
    
    def test_deadline_with_requirements(self):
        """Test Deadline model with submission requirements."""
        requirement1 = SubmissionRequirement(
            requirement_id="req-1",
            title="Project Description",
            description="Must have detailed project description",
            required=True,
            completed=True
        )
        
        requirement2 = SubmissionRequirement(
            requirement_id="req-2",
            title="Demo Video",
            description="Must include demo video",
            required=True,
            completed=False
        )
        
        deadline = Deadline(
            hackathon_id="hack-123",
            project_id="proj-456",
            deadline_type=DeadlineType.SUBMISSION,
            deadline_time=datetime.now() + timedelta(days=3),
            requirements=[requirement1, requirement2],
            notification_schedule=[
                NotificationTiming.THREE_DAYS,
                NotificationTiming.ONE_DAY,
                NotificationTiming.ONE_HOUR
            ]
        )
        
        assert len(deadline.requirements) == 2
        assert len(deadline.notification_schedule) == 3
        assert deadline.requirements[0].completed
        assert not deadline.requirements[1].completed
    
    def test_devpost_project_with_full_data(self):
        """Test DevpostProject with complete data."""
        team_member = TeamMember(
            name="Alice Smith",
            email="alice@example.com",
            role="Lead Developer"
        )
        
        project_link = ProjectLink(
            title="GitHub Repository",
            url="https://github.com/user/project",
            link_type="github"
        )
        
        media_file = MediaFile(
            filename="demo.mp4",
            file_path=Path("media/demo.mp4"),
            media_type=MediaType.VIDEO,
            caption="Project demonstration video"
        )
        
        requirement = SubmissionRequirement(
            requirement_id="req-1",
            title="Project Demo",
            description="Must include working demo",
            required=True,
            completed=True
        )
        
        project = DevpostProject(
            id="proj-123",
            title="Amazing Hackathon Project",
            tagline="Solving real-world problems with AI",
            description="This project uses advanced AI techniques to solve important problems in the healthcare domain.",
            hackathon_id="hack-456",
            hackathon_name="AI for Good Hackathon",
            team_members=[team_member],
            tags=["ai", "healthcare", "python"],
            links=[project_link],
            media=[media_file],
            submission_requirements=[requirement],
            submission_status=SubmissionStatus.SUBMITTED,
            created_at=datetime.now() - timedelta(days=5),
            updated_at=datetime.now() - timedelta(hours=2),
            deadline=datetime.now() + timedelta(days=2)
        )
        
        assert len(project.team_members) == 1
        assert len(project.tags) == 3
        assert len(project.links) == 1
        assert len(project.media) == 1
        assert len(project.submission_requirements) == 1
        assert project.submission_status == SubmissionStatus.SUBMITTED
        assert project.team_members[0].name == "Alice Smith"
        assert project.links[0].link_type == "github"
        assert project.media[0].media_type == MediaType.VIDEO
        assert project.submission_requirements[0].completed


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

    pytest.main([__file__, "-v"])