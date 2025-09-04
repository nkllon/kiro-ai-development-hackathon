"""
Unit tests for Devpost validation.
"""

import pytest
from pathlib import Path

from src.beast_mode.integration.devpost.validation import DevpostValidator
from src.beast_mode.integration.devpost.models import ProjectMetadata, DevpostProject, TeamMember


class TestDevpostValidator:
    """Test cases for DevpostValidator."""
    
    def test_validate_valid_metadata(self):
        """Test validation of valid metadata."""
        metadata = ProjectMetadata(
            title="Test Project",
            tagline="A comprehensive test project",
            description="This is a detailed description of the test project that meets the minimum length requirements for Devpost submissions.",
            tags=["python", "testing"],
            team_members=["user1"],
            repository_url="https://github.com/user/project"
        )
        
        result = DevpostValidator.validate_project_metadata(metadata)
        
        assert result.is_valid is True
        assert len(result.validation_errors) == 0
        assert len(result.missing_fields) == 0
    
    def test_validate_missing_required_fields(self):
        """Test validation with missing required fields."""
        metadata = ProjectMetadata(
            title="",  # Empty title
            tagline="",  # Empty tagline
            description=""  # Empty description
        )
        
        result = DevpostValidator.validate_project_metadata(metadata)
        
        assert result.is_valid is False
        assert "title" in result.missing_fields
        assert "tagline" in result.missing_fields
        assert "description" in result.missing_fields
    
    def test_validate_title_length(self):
        """Test title length validation."""
        # Too short
        metadata = ProjectMetadata(
            title="Hi",  # Too short
            tagline="A test project",
            description="This is a detailed description that meets the minimum length requirements."
        )
        
        result = DevpostValidator.validate_project_metadata(metadata)
        assert result.is_valid is False
        assert any("at least" in error for error in result.validation_errors)
        
        # Too long
        metadata.title = "x" * 101  # Too long
        result = DevpostValidator.validate_project_metadata(metadata)
        assert result.is_valid is False
        assert any("no more than" in error for error in result.validation_errors)
    
    def test_validate_tagline_length(self):
        """Test tagline length validation."""
        metadata = ProjectMetadata(
            title="Test Project",
            tagline="x" * 121,  # Too long
            description="This is a detailed description that meets the minimum length requirements."
        )
        
        result = DevpostValidator.validate_project_metadata(metadata)
        assert result.is_valid is False
        assert any("Tagline must be no more than" in error for error in result.validation_errors)
    
    def test_validate_description_length(self):
        """Test description length validation."""
        # Too short
        metadata = ProjectMetadata(
            title="Test Project",
            tagline="A test project",
            description="Short"  # Too short
        )
        
        result = DevpostValidator.validate_project_metadata(metadata)
        assert result.is_valid is False
        assert any("at least" in error for error in result.validation_errors)
        
        # Too long
        metadata.description = "x" * 5001  # Too long
        result = DevpostValidator.validate_project_metadata(metadata)
        assert result.is_valid is False
        assert any("no more than" in error for error in result.validation_errors)
    
    def test_validate_url_format(self):
        """Test URL format validation."""
        metadata = ProjectMetadata(
            title="Test Project",
            tagline="A test project",
            description="This is a detailed description that meets the minimum length requirements.",
            repository_url="invalid-url"  # Invalid URL
        )
        
        result = DevpostValidator.validate_project_metadata(metadata)
        assert result.is_valid is False
        assert any("Repository URL is not valid" in error for error in result.validation_errors)
    
    def test_validate_tags_limit(self):
        """Test tags limit validation."""
        metadata = ProjectMetadata(
            title="Test Project",
            tagline="A test project",
            description="This is a detailed description that meets the minimum length requirements.",
            tags=["tag" + str(i) for i in range(11)]  # Too many tags
        )
        
        result = DevpostValidator.validate_project_metadata(metadata)
        assert result.is_valid is False
        assert any("Maximum" in error and "tags" in error for error in result.validation_errors)
    
    def test_validate_team_members_limit(self):
        """Test team members limit validation."""
        metadata = ProjectMetadata(
            title="Test Project",
            tagline="A test project",
            description="This is a detailed description that meets the minimum length requirements.",
            team_members=["user" + str(i) for i in range(11)]  # Too many members
        )
        
        result = DevpostValidator.validate_project_metadata(metadata)
        assert result.is_valid is False
        assert any("Maximum" in error and "team members" in error for error in result.validation_errors)
    
    def test_validate_warnings(self):
        """Test validation warnings for optional fields."""
        metadata = ProjectMetadata(
            title="Test Project",
            tagline="A test project",
            description="This is a detailed description that meets the minimum length requirements."
            # No repository URL or tags
        )
        
        result = DevpostValidator.validate_project_metadata(metadata)
        assert result.is_valid is True  # Still valid
        assert len(result.warnings) > 0
        assert any("Repository URL is recommended" in warning for warning in result.warnings)
        assert any("Tags help with" in warning for warning in result.warnings)
    
    def test_validate_devpost_project(self):
        """Test validation of DevpostProject."""
        project = DevpostProject(
            id="test-123",
            title="Test Project",
            tagline="A comprehensive test project",
            description="This is a detailed description of the test project that meets the minimum length requirements for Devpost submissions.",
            hackathon_id="hack-456",
            hackathon_name="Test Hackathon",
            team_members=[TeamMember(username="user1", display_name="User One")]
        )
        
        result = DevpostValidator.validate_devpost_project(project)
        assert result.is_valid is True
    
    def test_validate_file_paths(self):
        """Test file paths validation."""
        file_paths = [
            Path("README.md"),
            Path("package.json"),
            Path("src/main.py")
        ]
        
        result = DevpostValidator.validate_file_paths(file_paths)
        assert result.is_valid is True
        assert len(result.missing_fields) == 0
    
    def test_validate_missing_readme(self):
        """Test validation with missing README."""
        file_paths = [
            Path("package.json"),
            Path("src/main.py")
        ]
        
        result = DevpostValidator.validate_file_paths(file_paths)
        assert result.is_valid is False
        assert "README file" in result.missing_fields
    
    def test_get_validation_requirements(self):
        """Test getting validation requirements."""
        requirements = DevpostValidator.get_validation_requirements()
        
        assert "title" in requirements
        assert "tagline" in requirements
        assert "description" in requirements
        assert requirements["title"]["required"] is True
        assert requirements["title"]["min_length"] == 3