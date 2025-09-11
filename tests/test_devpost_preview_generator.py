#!/usr/bin/env python3
"""
Unit tests for Devpost Preview Generator

Tests the complete preview generation system including:
- HTML template rendering using Jinja2
- Preview data collection from local project files
- Devpost-style CSS and layout matching
- Preview validation against Devpost requirements
- Real-time preview updates
- Preview export functionality
- Missing field highlighting and validation feedback

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
"""

import json
import tempfile
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.devpost_integration.preview_generator import (
    DevpostPreviewGenerator, RealtimePreviewManager
)
from src.devpost_integration.models import (
    ProjectMetadata, ValidationResult, PreviewData, FormattingIssue,
    MediaFile, MediaType, FileChangeEvent, ChangeType, ContentType
)
from src.devpost_integration.validation_engine import ValidationEngine


class TestDevpostPreviewGenerator:
    """Test suite for DevpostPreviewGenerator class."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory with sample files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create sample README.md
            readme_content = """# Beast Mode Framework

Where Requirements ARE the Solution

This is a comprehensive AI-powered development framework that enables systematic, 
specification-driven software development. The system provides seamless project 
management capabilities with real-time synchronization and automated validation.

## Features

- Systematic development methodology
- AI-powered code generation
- Requirements-driven architecture
- Comprehensive validation system

## Team

- Development Team Lead
- AI Systems Architect
- Quality Assurance Engineer

## Technologies

Built with Python, TypeScript, and systematic engineering practices.
"""
            (project_path / 'README.md').write_text(readme_content)
            
            # Create sample package.json
            package_data = {
                "name": "beast-mode-framework",
                "version": "1.0.0",
                "description": "AI-powered systematic development framework",
                "keywords": ["ai", "development", "systematic", "framework"],
                "author": "Beast Mode Team",
                "repository": {
                    "type": "git",
                    "url": "https://github.com/beast-mode/framework.git"
                }
            }
            (project_path / 'package.json').write_text(json.dumps(package_data, indent=2))
            
            # Create sample media files
            (project_path / 'screenshot.png').write_text("fake image data")
            (project_path / 'demo.mp4').write_text("fake video data")
            
            # Create requirements.txt to indicate Python project
            (project_path / 'requirements.txt').write_text("pytest>=7.0.0\nrequests>=2.28.0")
            
            yield project_path
    
    @pytest.fixture
    def mock_validation_engine(self):
        """Create mock validation engine."""
        engine = Mock()
        
        # Mock the validation report
        mock_report = Mock()
        mock_report.is_valid = True
        mock_report.completion_percentage = 85.0
        mock_report.missing_fields = []
        mock_report.get_issues_by_severity.return_value = []
        
        engine.validate_metadata.return_value = mock_report
        return engine
    
    @pytest.fixture
    def preview_generator(self, temp_project_dir, mock_validation_engine):
        """Create DevpostPreviewGenerator instance."""
        return DevpostPreviewGenerator(
            project_path=temp_project_dir,
            validation_engine=mock_validation_engine
        )
    
    def test_initialization(self, temp_project_dir):
        """Test preview generator initialization."""
        generator = DevpostPreviewGenerator(project_path=temp_project_dir)
        
        assert generator.project_path == temp_project_dir
        assert generator.validation_engine is not None
        assert generator._project_data_cache is None
        assert generator._cache_timestamp is None
    
    def test_project_title_extraction(self, preview_generator):
        """Test project title extraction from README."""
        title = preview_generator._extract_project_title()
        assert title == "Beast Mode Framework"
    
    def test_project_tagline_extraction(self, preview_generator):
        """Test project tagline extraction from README."""
        tagline = preview_generator._extract_project_tagline()
        assert "Requirements ARE the Solution" in tagline
    
    def test_project_description_extraction(self, preview_generator):
        """Test project description extraction from README."""
        description = preview_generator._extract_project_description()
        assert "AI-powered development framework" in description
        assert "systematic" in description.lower()
    
    def test_project_tags_extraction(self, preview_generator):
        """Test project tags extraction from various sources."""
        tags = preview_generator._extract_project_tags()
        
        # Should include tags from package.json keywords
        assert "ai" in tags
        assert "framework" in tags
        
        # Should include technology detection
        assert "python" in tags  # From requirements.txt
        
        # Should include systematic tags
        assert "systematic-development" in tags
    
    def test_team_members_extraction(self, preview_generator):
        """Test team member extraction from README."""
        team_members = preview_generator._extract_team_members()
        
        assert len(team_members) > 0
        assert any("Team Lead" in member for member in team_members)
    
    def test_repository_url_extraction(self, preview_generator):
        """Test repository URL extraction from package.json."""
        repo_url = preview_generator._extract_repository_url()
        assert repo_url == "https://github.com/beast-mode/framework.git"
    
    def test_technology_detection(self, preview_generator):
        """Test technology stack detection."""
        technologies = preview_generator._detect_technologies()
        
        assert "python" in technologies  # From requirements.txt
        assert "javascript" in technologies  # From package.json
    
    def test_media_files_collection(self, preview_generator):
        """Test media files collection from project directory."""
        media_files = preview_generator._collect_media_files()
        
        assert len(media_files) >= 2
        
        # Check for image file
        image_files = [f for f in media_files if f.media_type == MediaType.IMAGE]
        assert len(image_files) >= 1
        assert any(f.filename == "screenshot.png" for f in image_files)
        
        # Check for video file
        video_files = [f for f in media_files if f.media_type == MediaType.VIDEO]
        assert len(video_files) >= 1
        assert any(f.filename == "demo.mp4" for f in video_files)
    
    def test_project_metadata_collection(self, preview_generator):
        """Test complete project metadata collection."""
        metadata = preview_generator._collect_project_metadata()
        
        assert isinstance(metadata, ProjectMetadata)
        assert metadata.title == "Beast Mode Framework"
        assert "Requirements ARE the Solution" in metadata.tagline
        assert len(metadata.description) > 100
        assert len(metadata.tags) > 0
        assert len(metadata.team_members) > 0
        assert metadata.repository_url is not None
    
    def test_metadata_caching(self, preview_generator):
        """Test metadata caching functionality."""
        # First call should populate cache
        metadata1 = preview_generator._collect_project_metadata()
        assert preview_generator._project_data_cache is not None
        assert preview_generator._cache_timestamp is not None
        
        # Second call should use cache
        metadata2 = preview_generator._collect_project_metadata()
        assert metadata1.title == metadata2.title
        
        # Cache should expire after TTL
        preview_generator._cache_timestamp = datetime.now() - timedelta(seconds=400)
        metadata3 = preview_generator._collect_project_metadata()
        assert metadata3.title == metadata1.title  # Should still work
    
    def test_validation_integration(self, preview_generator, mock_validation_engine):
        """Test validation engine integration."""
        metadata = ProjectMetadata(
            title="Test Project",
            tagline="Test tagline for validation",
            description="Test description that is long enough to pass validation requirements"
        )
        
        validation_result = preview_generator.validate_project_requirements(metadata)
        
        assert isinstance(validation_result, ValidationResult)
        mock_validation_engine.validate_metadata.assert_called_once()
    
    def test_missing_fields_highlighting(self, preview_generator):
        """Test missing field highlighting functionality."""
        # Test with incomplete metadata
        incomplete_metadata = ProjectMetadata(
            title="",  # Missing title
            tagline="Short",  # Too short
            description=""  # Missing description
        )
        
        issues = preview_generator.highlight_missing_fields(incomplete_metadata)
        
        assert len(issues) > 0
        
        # Check for title issue
        title_issues = [i for i in issues if i.field_name == 'title']
        assert len(title_issues) > 0
        assert title_issues[0].severity == 'error'
        
        # Check for tagline issue
        tagline_issues = [i for i in issues if i.field_name == 'tagline']
        assert len(tagline_issues) > 0
        
        # Check for description issue
        description_issues = [i for i in issues if i.field_name == 'description']
        assert len(description_issues) > 0
    
    def test_preview_generation_basic(self, preview_generator, temp_project_dir):
        """Test basic preview generation."""
        output_file = temp_project_dir / 'preview.html'
        
        preview_data = preview_generator.generate_preview(
            output_file=output_file,
            include_validation=True
        )
        
        assert isinstance(preview_data, PreviewData)
        assert preview_data.project_metadata.title == "Beast Mode Framework"
        assert preview_data.validation_result is not None
        assert len(preview_data.media_files) >= 0
        assert output_file.exists()
        
        # Check HTML content
        html_content = output_file.read_text()
        assert "Beast Mode Framework" in html_content
        assert "Requirements ARE the Solution" in html_content
        assert "<!DOCTYPE html>" in html_content
    
    @patch('src.devpost_integration.preview_generator.JINJA2_AVAILABLE', False)
    def test_fallback_template_rendering(self, preview_generator, temp_project_dir):
        """Test fallback template rendering when Jinja2 is not available."""
        output_file = temp_project_dir / 'preview_fallback.html'
        
        preview_data = preview_generator.generate_preview(output_file=output_file)
        
        assert output_file.exists()
        html_content = output_file.read_text()
        assert "Beast Mode Framework" in html_content
        assert "<!DOCTYPE html>" in html_content
    
    def test_builtin_template_rendering(self, preview_generator):
        """Test built-in template rendering."""
        metadata = ProjectMetadata(
            title="Test Project",
            tagline="Test tagline",
            description="Test description"
        )
        
        validation_result = ValidationResult(
            is_valid=True,
            completion_percentage=90.0,
            errors=[],
            warnings=["Test warning"]
        )
        
        template_data = {
            'metadata': metadata,
            'validation': validation_result,
            'media_files': [],
            'formatting_issues': [],
            'tech_stack': 'Python, JavaScript',
            'generated_at': datetime.now()
        }
        
        html_content = preview_generator._render_builtin_template(template_data)
        
        assert "Test Project" in html_content
        assert "Test tagline" in html_content
        assert "Test description" in html_content
        assert "Test warning" in html_content
        assert "90.0%" in html_content


class TestRealtimePreviewManager:
    """Test suite for RealtimePreviewManager class."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create basic README
            (project_path / 'README.md').write_text("# Test Project\n\nTest description")
            
            yield project_path
    
    @pytest.fixture
    def mock_preview_generator(self):
        """Create mock preview generator."""
        generator = Mock()
        generator._collect_project_metadata.return_value = ProjectMetadata(
            title="Test Project",
            tagline="Test tagline",
            description="Test description"
        )
        generator.generate_preview.return_value = PreviewData(
            project_metadata=ProjectMetadata(
                title="Test Project",
                tagline="Test tagline", 
                description="Test description"
            ),
            validation_result=ValidationResult(is_valid=True, completion_percentage=85.0),
            media_files=[],
            generated_at=datetime.now()
        )
        generator._project_data_cache = None
        generator._cache_timestamp = None
        generator._detect_technologies.return_value = ["python", "javascript"]
        generator._collect_media_files.return_value = []
        generator._render_template.return_value = "<!DOCTYPE html><html><body>Test Preview</body></html>"
        return generator
    
    @pytest.fixture
    def realtime_manager(self, mock_preview_generator, temp_project_dir):
        """Create RealtimePreviewManager instance."""
        return RealtimePreviewManager(
            preview_generator=mock_preview_generator,
            output_dir=temp_project_dir / 'previews'
        )
    
    def test_initialization(self, mock_preview_generator, temp_project_dir):
        """Test realtime preview manager initialization."""
        manager = RealtimePreviewManager(
            preview_generator=mock_preview_generator,
            output_dir=temp_project_dir / 'previews'
        )
        
        assert manager.preview_generator == mock_preview_generator
        assert manager.output_dir == temp_project_dir / 'previews'
        assert manager._last_update is None
        assert manager._pending_updates == []
    
    def test_relevant_changes_filtering(self, realtime_manager, temp_project_dir):
        """Test filtering of relevant file changes."""
        changes = [
            FileChangeEvent(
                file_path=temp_project_dir / 'README.md',
                change_type=ChangeType.MODIFIED,
                content_type=ContentType.DOCUMENTATION
            ),
            FileChangeEvent(
                file_path=temp_project_dir / 'src' / 'main.py',
                change_type=ChangeType.MODIFIED,
                content_type=ContentType.SOURCE_CODE
            ),
            FileChangeEvent(
                file_path=temp_project_dir / 'package.json',
                change_type=ChangeType.MODIFIED,
                content_type=ContentType.CONFIGURATION
            ),
            FileChangeEvent(
                file_path=temp_project_dir / '.git' / 'config',
                change_type=ChangeType.MODIFIED,
                content_type=ContentType.CONFIGURATION
            )
        ]
        
        relevant_changes = realtime_manager._filter_relevant_changes(changes)
        
        # Should include README.md and package.json, but not .git/config or main.py
        assert len(relevant_changes) >= 2
        
        relevant_paths = [str(change.file_path.name) for change in relevant_changes]
        assert 'README.md' in relevant_paths
        assert 'package.json' in relevant_paths
    
    def test_realtime_preview_update(self, realtime_manager, temp_project_dir):
        """Test real-time preview updates."""
        changes = [
            FileChangeEvent(
                file_path=temp_project_dir / 'README.md',
                change_type=ChangeType.MODIFIED,
                content_type=ContentType.DOCUMENTATION
            )
        ]
        
        preview_data = realtime_manager.update_preview_realtime(changes)
        
        assert isinstance(preview_data, PreviewData)
        assert realtime_manager._last_update is not None
        assert len(realtime_manager._pending_updates) == 0
    
    def test_update_debouncing(self, realtime_manager, temp_project_dir):
        """Test update debouncing functionality."""
        changes = [
            FileChangeEvent(
                file_path=temp_project_dir / 'README.md',
                change_type=ChangeType.MODIFIED,
                content_type=ContentType.DOCUMENTATION
            )
        ]
        
        # First update
        realtime_manager.update_preview_realtime(changes)
        first_update_time = realtime_manager._last_update
        
        # Immediate second update should be debounced
        realtime_manager.update_preview_realtime(changes)
        
        assert realtime_manager._last_update == first_update_time
        assert len(realtime_manager._pending_updates) > 0
    
    def test_html_export(self, realtime_manager, temp_project_dir):
        """Test HTML export functionality."""
        export_path = realtime_manager.export_preview_offline(
            export_name="test_export",
            format_type="html",
            include_assets=True
        )
        
        assert export_path.exists()
        assert export_path.suffix == '.html'
        assert "test_export" in export_path.name
        
        # Check HTML content
        html_content = export_path.read_text()
        assert "<!DOCTYPE html>" in html_content
    
    def test_markdown_export(self, realtime_manager, temp_project_dir):
        """Test Markdown export functionality."""
        export_path = realtime_manager.export_preview_offline(
            export_name="test_export",
            format_type="markdown"
        )
        
        assert export_path.exists()
        assert export_path.suffix == '.md'
        
        # Check Markdown content
        md_content = export_path.read_text()
        assert "# Test Project" in md_content
        assert "## Description" in md_content
    
    def test_validation_feedback(self, realtime_manager):
        """Test validation feedback generation."""
        feedback = realtime_manager.get_validation_feedback(include_suggestions=True)
        
        assert 'overall_score' in feedback
        assert 'is_ready_for_submission' in feedback
        assert 'validation_summary' in feedback
        assert 'issues' in feedback
        assert 'next_steps' in feedback
        
        # Check validation summary structure
        summary = feedback['validation_summary']
        assert 'total_checks' in summary
        assert 'passed_checks' in summary
        assert 'critical_issues' in summary
    
    def test_completion_breakdown(self, realtime_manager):
        """Test completion breakdown calculation."""
        metadata = ProjectMetadata(
            title="Complete Project",
            tagline="This is a complete tagline for testing",
            description="This is a complete description that is long enough to pass validation requirements and provide good detail about the project",
            tags=["python", "testing"],
            team_members=["Developer"],
            repository_url="https://github.com/test/repo"
        )
        
        validation = ValidationResult(is_valid=True, completion_percentage=95.0)
        
        breakdown = realtime_manager._get_completion_breakdown(metadata, validation)
        
        assert 'required_fields' in breakdown
        assert 'optional_fields' in breakdown
        assert 'percentages' in breakdown
        
        # Check required fields
        required = breakdown['required_fields']
        assert required['title'] is True
        assert required['tagline'] is True
        assert required['description'] is True
        
        # Check percentages
        percentages = breakdown['percentages']
        assert percentages['required_fields'] == 100.0
        assert percentages['overall'] > 0
    
    def test_next_steps_generation(self, realtime_manager):
        """Test next steps generation."""
        critical_issues = [
            FormattingIssue(
                field_name="title",
                issue_type="missing_required",
                description="Title is required",
                severity="error",
                suggested_fix="Add a project title"
            )
        ]
        
        warning_issues = [
            FormattingIssue(
                field_name="tags",
                issue_type="missing_content",
                description="No tags specified",
                severity="warning",
                suggested_fix="Add relevant tags"
            )
        ]
        
        next_steps = realtime_manager._generate_next_steps(critical_issues, warning_issues)
        
        assert len(next_steps) > 0
        assert any("Add a project title" in step for step in next_steps)
        assert any("Add relevant tags" in step for step in next_steps)
    
    def test_export_history_tracking(self, realtime_manager):
        """Test export history tracking."""
        # Perform an export
        realtime_manager.export_preview_offline(
            export_name="history_test",
            format_type="html"
        )
        
        history = realtime_manager.get_export_history()
        
        assert len(history) == 1
        assert history[0]['format_type'] == 'html'
        assert 'timestamp' in history[0]
        assert 'export_path' in history[0]
    
    def test_cached_preview_data_fallback(self, realtime_manager):
        """Test cached preview data fallback."""
        # Test when no cache exists
        cached_data = realtime_manager._get_cached_preview_data()
        
        assert isinstance(cached_data, PreviewData)
        assert cached_data.project_metadata.title is not None
    
    def test_error_handling_in_realtime_update(self, realtime_manager, temp_project_dir):
        """Test error handling in real-time updates."""
        # Mock an error in preview generation
        realtime_manager.preview_generator.generate_preview.side_effect = Exception("Test error")
        
        changes = [
            FileChangeEvent(
                file_path=temp_project_dir / 'README.md',
                change_type=ChangeType.MODIFIED,
                content_type=ContentType.DOCUMENTATION
            )
        ]
        
        # Should not raise exception, should return cached data
        preview_data = realtime_manager.update_preview_realtime(changes)
        
        assert isinstance(preview_data, PreviewData)
    
    def test_export_with_assets(self, realtime_manager, temp_project_dir):
        """Test export with asset copying."""
        # Create a fake media file
        media_dir = temp_project_dir / 'media'
        media_dir.mkdir()
        test_image = media_dir / 'test.png'
        test_image.write_text("fake image data")
        
        # Mock media files in preview data
        media_file = MediaFile(
            filename="test.png",
            file_path=test_image,
            media_type=MediaType.IMAGE
        )
        
        realtime_manager.preview_generator.generate_preview.return_value.media_files = [media_file]
        
        export_path = realtime_manager.export_preview_offline(
            export_name="assets_test",
            format_type="html",
            include_assets=True
        )
        
        assert export_path.exists()
        
        # Check if assets directory was created
        assets_dir = export_path.parent / 'assets'
        assert assets_dir.exists()


if __name__ == '__main__':
    pytest.main([__file__])