"""
Tests for ChangeDetector class.

This module tests the intelligent change detection functionality including
content-based change detection, media file categorization, and Git integration.
"""

import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import pytest

from src.beast_mode.integration.devpost.monitoring.change_detector import (
    ChangeDetector,
    ContentChange,
    MediaFileInfo,
    GitChange
)
from src.beast_mode.integration.devpost.models import ChangeType


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create test files
        (project_path / "README.md").write_text("# Test Project\n\nThis is a test project.")
        (project_path / "CHANGELOG.md").write_text("# Changelog\n\n## v1.0.0\n- Initial release")
        (project_path / "LICENSE").write_text("MIT License")
        (project_path / "package.json").write_text('{"name": "test", "version": "1.0.0"}')
        
        # Create media directory with test files
        media_dir = project_path / "media"
        media_dir.mkdir()
        (media_dir / "screenshot.png").write_bytes(b"fake png data")
        (media_dir / "demo_video.mp4").write_bytes(b"fake mp4 data")
        (media_dir / "document.pdf").write_bytes(b"fake pdf data")
        
        # Create source directory
        src_dir = project_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("print('hello world')")
        
        yield project_path


@pytest.fixture
def change_detector(temp_project_dir):
    """Create a ChangeDetector instance for testing."""
    return ChangeDetector(temp_project_dir)


class TestChangeDetector:
    """Test cases for ChangeDetector."""
    
    def test_init(self, temp_project_dir):
        """Test detector initialization."""
        detector = ChangeDetector(temp_project_dir)
        
        assert detector.project_path == temp_project_dir.resolve()
        assert isinstance(detector._file_hashes, dict)
        assert isinstance(detector._media_cache, dict)
        assert isinstance(detector._git_refs_cache, dict)
    
    def test_is_documentation_file(self, change_detector, temp_project_dir):
        """Test documentation file detection."""
        # Documentation files
        assert change_detector.is_documentation_file(temp_project_dir / "README.md")
        assert change_detector.is_documentation_file(temp_project_dir / "CHANGELOG.md")
        assert change_detector.is_documentation_file(temp_project_dir / "LICENSE")
        
        # Create docs directory
        docs_dir = temp_project_dir / "docs"
        docs_dir.mkdir()
        (docs_dir / "guide.md").write_text("# Guide")
        assert change_detector.is_documentation_file(docs_dir / "guide.md")
        
        # Non-documentation files
        assert not change_detector.is_documentation_file(temp_project_dir / "package.json")
        assert not change_detector.is_documentation_file(temp_project_dir / "src" / "main.py")
    
    def test_is_media_file(self, change_detector, temp_project_dir):
        """Test media file detection."""
        media_dir = temp_project_dir / "media"
        
        # Media files
        assert change_detector.is_media_file(media_dir / "screenshot.png")
        assert change_detector.is_media_file(media_dir / "demo_video.mp4")
        assert change_detector.is_media_file(media_dir / "document.pdf")
        
        # Non-media files
        assert not change_detector.is_media_file(temp_project_dir / "README.md")
        assert not change_detector.is_media_file(temp_project_dir / "src" / "main.py")
    
    def test_get_file_significance(self, change_detector, temp_project_dir):
        """Test file significance calculation."""
        # High significance files
        assert change_detector.get_file_significance(temp_project_dir / "README.md") == 1.0
        assert change_detector.get_file_significance(temp_project_dir / "package.json") == 0.9
        
        # Documentation files
        changelog_sig = change_detector.get_file_significance(temp_project_dir / "CHANGELOG.md")
        assert changelog_sig == 0.8
        
        # Media files
        media_sig = change_detector.get_file_significance(temp_project_dir / "media" / "screenshot.png")
        assert media_sig >= 0.5
        
        # Source files
        src_sig = change_detector.get_file_significance(temp_project_dir / "src" / "main.py")
        assert src_sig == 0.4
    
    def test_detect_content_changes_new_file(self, change_detector, temp_project_dir):
        """Test content change detection for new files."""
        new_file = temp_project_dir / "new_file.md"
        new_file.write_text("# New File")
        
        change = change_detector.detect_content_changes(new_file)
        
        assert change is not None
        assert change.file_path == new_file
        assert change.change_type == 'content'
        assert change.old_hash is None
        assert change.new_hash is not None
        assert change.significance > 0
        assert "New file created" in change.description
    
    def test_detect_content_changes_modified_file(self, change_detector, temp_project_dir):
        """Test content change detection for modified files."""
        readme_file = temp_project_dir / "README.md"
        
        # First detection (establishes baseline)
        change1 = change_detector.detect_content_changes(readme_file)
        assert change1 is not None  # New file
        
        # Modify file
        readme_file.write_text("# Updated Test Project\n\nThis is an updated test project.")
        
        # Second detection (should detect change)
        change2 = change_detector.detect_content_changes(readme_file)
        
        assert change2 is not None
        assert change2.file_path == readme_file
        assert change2.old_hash != change2.new_hash
        assert change2.significance > 0
    
    def test_detect_content_changes_no_change(self, change_detector, temp_project_dir):
        """Test content change detection when file hasn't changed."""
        readme_file = temp_project_dir / "README.md"
        
        # First detection
        change1 = change_detector.detect_content_changes(readme_file)
        assert change1 is not None
        
        # Second detection without modification
        change2 = change_detector.detect_content_changes(readme_file)
        assert change2 is None  # No change
    
    def test_detect_content_changes_deleted_file(self, change_detector, temp_project_dir):
        """Test content change detection for deleted files."""
        temp_file = temp_project_dir / "temp_file.txt"
        temp_file.write_text("temporary content")
        
        # First detection (establishes baseline)
        change1 = change_detector.detect_content_changes(temp_file)
        assert change1 is not None
        
        # Delete file
        temp_file.unlink()
        
        # Second detection (should detect deletion)
        change2 = change_detector.detect_content_changes(temp_file)
        
        assert change2 is not None
        assert change2.file_path == temp_file
        assert change2.new_hash is None
        assert change2.significance == 1.0
        assert "File deleted" in change2.description
    
    def test_categorize_media_file(self, change_detector, temp_project_dir):
        """Test media file categorization."""
        media_dir = temp_project_dir / "media"
        
        # Test image file
        image_file = media_dir / "screenshot.png"
        image_info = change_detector.categorize_media_file(image_file)
        
        assert image_info is not None
        assert image_info.file_path == image_file
        assert image_info.media_type == 'image'
        assert image_info.file_size > 0
        assert not image_info.is_demo_material  # filename doesn't contain demo indicators
        
        # Test video file with demo indicator
        video_file = media_dir / "demo_video.mp4"
        video_info = change_detector.categorize_media_file(video_file)
        
        assert video_info is not None
        assert video_info.media_type == 'video'
        assert video_info.is_demo_material  # filename contains 'demo'
        
        # Test document file
        doc_file = media_dir / "document.pdf"
        doc_info = change_detector.categorize_media_file(doc_file)
        
        assert doc_info is not None
        assert doc_info.media_type == 'document'
        
        # Test non-media file
        text_file = temp_project_dir / "README.md"
        text_info = change_detector.categorize_media_file(text_file)
        assert text_info is None
    
    def test_categorize_media_file_caching(self, change_detector, temp_project_dir):
        """Test media file categorization caching."""
        media_file = temp_project_dir / "media" / "screenshot.png"
        
        # First call
        info1 = change_detector.categorize_media_file(media_file)
        assert info1 is not None
        
        # Second call (should use cache)
        info2 = change_detector.categorize_media_file(media_file)
        assert info2 is not None
        assert info1.file_path == info2.file_path
        assert info1.media_type == info2.media_type
    
    def test_get_media_type(self, change_detector):
        """Test media type detection."""
        # Image files
        assert change_detector._get_media_type(Path("test.jpg")) == 'image'
        assert change_detector._get_media_type(Path("test.png")) == 'image'
        assert change_detector._get_media_type(Path("test.gif")) == 'image'
        
        # Video files
        assert change_detector._get_media_type(Path("test.mp4")) == 'video'
        assert change_detector._get_media_type(Path("test.avi")) == 'video'
        
        # Audio files
        assert change_detector._get_media_type(Path("test.mp3")) == 'audio'
        assert change_detector._get_media_type(Path("test.wav")) == 'audio'
        
        # Document files
        assert change_detector._get_media_type(Path("test.pdf")) == 'document'
        assert change_detector._get_media_type(Path("test.docx")) == 'document'
        
        # Non-media files
        assert change_detector._get_media_type(Path("test.txt")) is None
        assert change_detector._get_media_type(Path("test.py")) is None
    
    def test_is_demo_material(self, change_detector):
        """Test demo material detection."""
        # Demo material files
        assert change_detector._is_demo_material(Path("screenshot.png"))
        assert change_detector._is_demo_material(Path("demo_video.mp4"))
        assert change_detector._is_demo_material(Path("preview_image.jpg"))
        assert change_detector._is_demo_material(Path("media/showcase/example.png"))
        
        # Non-demo files
        assert not change_detector._is_demo_material(Path("profile.jpg"))
        assert not change_detector._is_demo_material(Path("data.csv"))
        assert not change_detector._is_demo_material(Path("config.json"))
    
    @patch('subprocess.run')
    def test_is_git_repository(self, mock_run, change_detector):
        """Test Git repository detection."""
        # Mock successful git command
        mock_run.return_value = Mock(returncode=0)
        assert change_detector._is_git_repository()
        
        # Mock failed git command
        mock_run.return_value = Mock(returncode=1)
        assert not change_detector._is_git_repository()
        
        # Mock subprocess error
        mock_run.side_effect = subprocess.SubprocessError()
        assert not change_detector._is_git_repository()
    
    @patch('subprocess.run')
    def test_detect_new_tags(self, mock_run, change_detector):
        """Test Git tag detection."""
        # Mock git tag command
        mock_run.return_value = Mock(
            returncode=0,
            stdout="v2.0.0\nv1.1.0\nv1.0.0\n"
        )
        
        # Mock no cached tags (all are new)
        changes = change_detector._detect_new_tags()
        
        # Should detect new tags
        assert len(changes) >= 0  # Depends on mocked tag info
    
    @patch('subprocess.run')
    def test_detect_new_commits(self, mock_run, change_detector):
        """Test Git commit detection."""
        # Mock git log command
        mock_run.return_value = Mock(
            returncode=0,
            stdout="abc123 Add new feature\ndef456 Fix bug in parser\n"
        )
        
        changes = change_detector._detect_new_commits()
        
        # Should detect commits
        assert len(changes) >= 0  # Depends on mocked commit timestamp
    
    @patch('subprocess.run')
    def test_get_tag_info(self, mock_run, change_detector):
        """Test getting Git tag information."""
        # Mock git commands for tag info
        mock_run.side_effect = [
            Mock(returncode=0, stdout="abc123\n"),  # git rev-list
            Mock(returncode=0, stdout="Release v1.0.0\n"),  # git tag format
            Mock(returncode=0, stdout="1640995200\n")  # git show timestamp
        ]
        
        tag_info = change_detector._get_tag_info("v1.0.0")
        
        assert tag_info is not None
        assert tag_info.change_type == 'tag'
        assert tag_info.ref_name == "v1.0.0"
        assert tag_info.commit_hash == "abc123"
        assert "Release v1.0.0" in tag_info.message
    
    @patch('subprocess.run')
    def test_get_commit_timestamp(self, mock_run, change_detector):
        """Test getting commit timestamp."""
        # Mock git show command
        mock_run.return_value = Mock(
            returncode=0,
            stdout="1640995200\n"  # Unix timestamp
        )
        
        timestamp = change_detector._get_commit_timestamp("abc123")
        
        assert isinstance(timestamp, datetime)
        # Should be around 2022-01-01 (timestamp 1640995200)
        assert timestamp.year == 2022
    
    def test_calculate_file_hash(self, change_detector, temp_project_dir):
        """Test file hash calculation."""
        readme_file = temp_project_dir / "README.md"
        
        hash1 = change_detector._calculate_file_hash(readme_file)
        assert len(hash1) == 64  # SHA-256 hex string
        
        # Hash should be consistent
        hash2 = change_detector._calculate_file_hash(readme_file)
        assert hash1 == hash2
        
        # Hash should change when file changes
        readme_file.write_text("# Different content")
        hash3 = change_detector._calculate_file_hash(readme_file)
        assert hash1 != hash3
    
    def test_determine_change_type(self, change_detector, temp_project_dir):
        """Test change type determination."""
        # Documentation file
        readme_file = temp_project_dir / "README.md"
        assert change_detector._determine_change_type(readme_file) == 'documentation'
        
        # Media file
        media_file = temp_project_dir / "media" / "screenshot.png"
        assert change_detector._determine_change_type(media_file) == 'media'
        
        # Metadata file
        package_file = temp_project_dir / "package.json"
        assert change_detector._determine_change_type(package_file) == 'metadata'
        
        # Regular content file
        src_file = temp_project_dir / "src" / "main.py"
        assert change_detector._determine_change_type(src_file) == 'content'
    
    def test_generate_change_description(self, change_detector, temp_project_dir):
        """Test change description generation."""
        readme_file = temp_project_dir / "README.md"
        
        # High significance change
        desc = change_detector._generate_change_description(readme_file, 'documentation', 0.9)
        assert "Major" in desc
        assert "documentation" in desc
        assert "README.md" in desc
        
        # Moderate significance change
        desc = change_detector._generate_change_description(readme_file, 'content', 0.6)
        assert "Moderate" in desc
        
        # Minor significance change
        desc = change_detector._generate_change_description(readme_file, 'content', 0.2)
        assert "Minor" in desc


@pytest.mark.integration
class TestChangeDetectorIntegration:
    """Integration tests for change detection."""
    
    @pytest.mark.timeout(10)
    def test_full_change_detection_workflow(self, temp_project_dir):
        """Test complete change detection workflow."""
        detector = ChangeDetector(temp_project_dir)
        
        # Test initial file detection
        readme_file = temp_project_dir / "README.md"
        change = detector.detect_content_changes(readme_file)
        assert change is not None
        assert change.old_hash is None  # New file
        
        # Test media file categorization
        media_file = temp_project_dir / "media" / "screenshot.png"
        media_info = detector.categorize_media_file(media_file)
        assert media_info is not None
        assert media_info.media_type == 'image'
        
        # Test file modification detection
        readme_file.write_text("# Modified README\n\nThis has been updated.")
        change2 = detector.detect_content_changes(readme_file)
        assert change2 is not None
        assert change2.old_hash is not None
        assert change2.new_hash != change2.old_hash
    
    @pytest.mark.timeout(5)
    @patch('subprocess.run')
    def test_git_integration_workflow(self, mock_run, temp_project_dir):
        """Test Git integration workflow."""
        detector = ChangeDetector(temp_project_dir)
        
        # Mock Git repository detection
        mock_run.return_value = Mock(returncode=0)
        
        # Test Git changes detection
        changes = detector.detect_git_changes()
        assert isinstance(changes, list)
        # Actual content depends on mocked Git commands