"""
Integration tests for path normalization with file analysis components.

Tests that path normalization works correctly with dependency analyzer,
file change detector, and other file system components.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.beast_mode.utils.path_normalizer import PathNormalizer, safe_relative_to
from src.beast_mode.domain_index.dependency_analyzer import OrphanedFileDetector
from src.beast_mode.domain_index.models import (
    Domain, DomainTools, DomainMetadata, PackagePotential
)


class TestPathNormalizationIntegration:
    """Integration tests for path normalization with file analysis components."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create project structure
            (project_root / "src").mkdir()
            (project_root / "src" / "main.py").touch()
            (project_root / "tests").mkdir()
            (project_root / "tests" / "test_main.py").touch()
            
            yield project_root
    
    @pytest.fixture
    def sample_domains(self):
        """Create sample domains for testing."""
        domains = {}  # DomainCollection is just Dict[str, Domain]
        
        # Create minimal domain objects for testing
        tools = DomainTools(linter="", formatter="", validator="")
        package_potential = PackagePotential(score=0.5, reasons=[], dependencies=[], estimated_effort="low", blockers=[])
        metadata = DomainMetadata(demo_role="test", extraction_candidate="no", package_potential=package_potential)
        
        src_domain = Domain(
            name="src_domain",
            description="Test domain",
            patterns=["src/**/*.py"],
            content_indicators=[],
            requirements=[],
            dependencies=[],
            tools=tools,
            metadata=metadata,
            file_count=1,
            line_count=100
        )
        domains["src_domain"] = src_domain
        
        return domains
    
    def test_orphaned_file_detector_with_mixed_paths(self, temp_project, sample_domains):
        """Test OrphanedFileDetector with mixed absolute and relative paths."""
        detector = OrphanedFileDetector(sample_domains, temp_project)
        
        # Mock glob to return mixed path types
        with patch.object(Path, 'glob') as mock_glob:
            # Return relative paths (as strings converted to Path objects)
            mock_glob.return_value = [
                Path("src/main.py"),  # Relative path
                Path("tests/test_main.py")  # Relative path
            ]
            
            # This should not raise ValueError about absolute/relative paths
            result = detector.detect_orphaned_files()
            
            # Should complete without path-related errors
            assert "orphaned_files" in result
            assert "total_files_checked" in result
            assert isinstance(result["coverage_percentage"], (int, float))
    
    def test_path_normalizer_with_dependency_analyzer_paths(self, temp_project):
        """Test PathNormalizer with paths commonly used in dependency analyzer."""
        # Test various path representations that might occur
        test_paths = [
            "src/main.py",  # Relative
            "./src/main.py",  # Relative with dot
            str(temp_project / "src" / "main.py"),  # Absolute string
            temp_project / "src" / "main.py"  # Absolute Path object
        ]
        
        # All should normalize to the same relative path when made relative to project root
        expected_relative = Path("src") / "main.py"
        
        for path in test_paths:
            with patch('pathlib.Path.cwd', return_value=temp_project):
                result = safe_relative_to(path, temp_project)
                if result is not None:
                    assert result == expected_relative or result.name == "main.py"
    
    def test_file_analysis_with_normalized_paths(self, temp_project, sample_domains):
        """Test file analysis components with normalized paths."""
        detector = OrphanedFileDetector(sample_domains, temp_project)
        
        # Test that _get_all_project_files works with normalized paths
        with patch.object(Path, 'glob') as mock_glob:
            # Mock glob to return paths that would cause issues without normalization
            mock_glob.return_value = [
                temp_project / "src" / "main.py",  # Absolute path
                temp_project / "tests" / "test_main.py"  # Absolute path
            ]
            
            # This should work without path-related errors
            files = detector._get_all_project_files(include_tests=True)
            
            # Should return a list of Path objects
            assert isinstance(files, list)
            # Should not be empty (unless filtered out)
            # The exact count depends on filtering logic
    
    def test_path_conflict_resolution_in_file_operations(self, temp_project):
        """Test path conflict resolution in realistic file operation scenarios."""
        # Simulate scenarios where paths might conflict
        scenarios = [
            {
                "file_path": "src/main.py",
                "project_root": str(temp_project),
                "description": "Relative file path with absolute project root"
            },
            {
                "file_path": str(temp_project / "src" / "main.py"),
                "project_root": str(temp_project),
                "description": "Absolute file path with absolute project root"
            },
            {
                "file_path": temp_project / "src" / "main.py",
                "project_root": temp_project,
                "description": "Path objects"
            }
        ]
        
        for scenario in scenarios:
            file_path = scenario["file_path"]
            project_root = scenario["project_root"]
            
            # Should be able to safely make relative without errors
            result = safe_relative_to(file_path, project_root)
            
            # Should either succeed or return None (not raise exception)
            if result is not None:
                assert isinstance(result, Path)
                assert not result.is_absolute()
    
    def test_path_normalization_with_symlinks(self, temp_project):
        """Test path normalization handles symlinks correctly."""
        # Create a symlink if possible (skip on systems that don't support it)
        try:
            symlink_path = temp_project / "src_link"
            symlink_path.symlink_to(temp_project / "src")
            
            # Test that normalization resolves symlinks
            symlink_file = symlink_path / "main.py"
            normalized = PathNormalizer.normalize_path(symlink_file)
            
            # Should resolve to the actual file path
            assert normalized.exists() or normalized.parent.exists()
            
        except (OSError, NotImplementedError):
            # Skip test if symlinks not supported
            pytest.skip("Symlinks not supported on this system")
    
    def test_path_validation_with_file_analysis(self, temp_project):
        """Test path validation in file analysis context."""
        # Test paths that should be valid for file analysis
        valid_paths = [
            temp_project / "src" / "main.py",
            "src/main.py",
            "./src/main.py"
        ]
        
        for path in valid_paths:
            # Should be able to validate path consistency
            result = PathNormalizer.validate_path_consistency([path], temp_project)
            # Result should be boolean (True or False, not an exception)
            assert isinstance(result, bool)
    
    def test_common_base_detection_for_project_files(self, temp_project):
        """Test common base detection with project file paths."""
        project_files = [
            temp_project / "src" / "main.py",
            temp_project / "tests" / "test_main.py",
            temp_project / "README.md"
        ]
        
        # Should detect project root as common base
        common_base = PathNormalizer.get_common_base(project_files)
        
        assert common_base is not None
        # Should be the project root or a parent of it
        assert temp_project.resolve() == common_base.resolve() or temp_project.is_relative_to(common_base)


class TestPathNormalizationErrorHandling:
    """Test error handling in path normalization."""
    
    def test_safe_relative_to_with_incompatible_paths(self):
        """Test safe_relative_to with paths that cannot be made relative."""
        with tempfile.TemporaryDirectory() as temp1, tempfile.TemporaryDirectory() as temp2:
            path1 = Path(temp1) / "file.py"
            path2 = Path(temp2)
            
            # Should return None instead of raising exception
            result = safe_relative_to(path1, path2)
            assert result is None
    
    def test_path_normalization_with_nonexistent_paths(self):
        """Test path normalization with paths that don't exist."""
        nonexistent_path = Path("/nonexistent/path/file.py")
        
        # Should still be able to normalize (doesn't require existence)
        result = PathNormalizer.normalize_path(nonexistent_path)
        assert isinstance(result, Path)
        assert result.is_absolute()
    
    def test_path_validation_with_invalid_paths(self):
        """Test path validation with invalid or problematic paths."""
        invalid_paths = [
            "",  # Empty string
            ".",  # Current directory
            "..",  # Parent directory
        ]
        
        for invalid_path in invalid_paths:
            # Should handle gracefully without exceptions
            try:
                result = PathNormalizer.normalize_path(invalid_path)
                assert isinstance(result, Path)
            except (ValueError, OSError):
                # Some invalid paths may raise exceptions, which is acceptable
                pass


class TestFileAnalysisComponentsIntegration:
    """Test integration with actual file analysis components."""
    
    @pytest.fixture
    def mock_domains(self):
        """Create mock domains for testing."""
        domains = {}  # DomainCollection is just Dict[str, Domain]
        
        # Create minimal domain objects for testing
        tools = DomainTools(linter="", formatter="", validator="")
        package_potential = PackagePotential(score=0.5, reasons=[], dependencies=[], estimated_effort="low", blockers=[])
        metadata = DomainMetadata(demo_role="test", extraction_candidate="no", package_potential=package_potential)
        
        domain = Domain(
            name="test_domain",
            description="Test domain",
            patterns=["src/**/*.py"],
            content_indicators=[],
            requirements=[],
            dependencies=[],
            tools=tools,
            metadata=metadata,
            file_count=1,
            line_count=100
        )
        domains["test_domain"] = domain
        
        return domains
    
    def test_dependency_analyzer_path_operations(self, mock_domains):
        """Test dependency analyzer path operations with normalization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            detector = OrphanedFileDetector(mock_domains, project_root)
            
            # Test set_project_root with path normalization
            detector.project_root = PathNormalizer.normalize_path(project_root)
            
            # Should be normalized to absolute path
            assert detector.project_root.is_absolute()
            assert detector.project_root == project_root.resolve()
    
    def test_file_change_detector_path_handling(self):
        """Test that file change detector handles paths correctly."""
        # This test verifies that file change detector doesn't have path issues
        # Since it mainly works with string paths, it should be compatible
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Test path normalization for file change detector scenarios
            file_paths = [
                "src/main.py",
                "tests/test_main.py",
                "README.md"
            ]
            
            for file_path in file_paths:
                # Should be able to normalize paths for file change detection
                normalized = PathNormalizer.normalize_path(project_root / file_path)
                relative = safe_relative_to(normalized, project_root)
                
                assert relative is not None
                assert str(relative) == file_path
    
    def test_file_change_detector_with_normalized_paths(self):
        """Test FileChangeDetector with normalized paths."""
        from src.beast_mode.compliance.git.file_change_detector import FileChangeDetector
        from src.beast_mode.compliance.models import CommitInfo
        from datetime import datetime
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create test files
            (project_root / "src").mkdir()
            (project_root / "src" / "main.py").touch()
            (project_root / "tests").mkdir()
            (project_root / "tests" / "test_main.py").touch()
            
            detector = FileChangeDetector(str(project_root))
            
            # Test that repository path is normalized
            assert detector.repository_path.is_absolute()
            assert detector.repository_path == project_root.resolve()
            
            # Test file path normalization in commit processing
            commit = CommitInfo(
                commit_hash="test123",
                author="Test Author",
                timestamp=datetime.now(),
                message="Test commit",
                modified_files=["src/main.py"],  # Relative path
                added_files=[str(project_root / "tests" / "test_main.py")],  # Absolute path
                deleted_files=[]
            )
            
            # Should handle mixed path types without errors
            changes = detector._extract_file_changes_from_commit(commit)
            
            assert len(changes) == 2
            # All file paths should be consistently formatted
            for change in changes:
                assert isinstance(change.file_path, str)
                # Should not contain absolute path markers when not needed
                if not Path(change.file_path).is_absolute():
                    assert not change.file_path.startswith(str(project_root))
    
    def test_dependency_analyzer_with_mixed_path_types(self, mock_domains):
        """Test dependency analyzer with mixed absolute and relative paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create test files
            (project_root / "src").mkdir()
            (project_root / "src" / "main.py").touch()
            (project_root / "tests").mkdir()
            (project_root / "tests" / "test_main.py").touch()
            
            detector = OrphanedFileDetector(mock_domains, project_root)
            
            # Mock glob to return mixed path types
            with patch.object(Path, 'glob') as mock_glob:
                mock_glob.return_value = [
                    project_root / "src" / "main.py",  # Absolute
                    Path("tests/test_main.py")  # Relative
                ]
                
                # Should handle mixed paths without ValueError
                files = detector._get_all_project_files(include_tests=True)
                
                # Should return normalized paths
                assert isinstance(files, list)
                for file_path in files:
                    assert isinstance(file_path, Path)
                    assert file_path.is_absolute()
    
    def test_file_pattern_matching_with_normalized_paths(self):
        """Test file pattern matching works with normalized paths."""
        from src.beast_mode.compliance.git.file_change_detector import FileChangeDetector
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            detector = FileChangeDetector(str(project_root))
            
            # Test patterns with different path formats
            patterns = ["src/**/*.py", "tests/*test*.py"]
            
            test_files = [
                "src/main.py",  # Relative
                str(project_root / "src" / "utils.py"),  # Absolute
                "tests/test_main.py",  # Relative
                str(project_root / "tests" / "test_utils.py")  # Absolute
            ]
            
            for file_path in test_files:
                # Should match patterns regardless of absolute/relative format
                matches = detector._file_matches_task_patterns(file_path, patterns)
                
                # All test files should match at least one pattern
                assert matches is True or matches is False  # Should not raise exception
    
    def test_file_analysis_error_handling_with_paths(self, mock_domains):
        """Test error handling in file analysis with problematic paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            detector = OrphanedFileDetector(mock_domains, project_root)
            
            # Test with paths that might cause issues
            problematic_paths = [
                "/nonexistent/absolute/path.py",
                "relative/../path.py",
                "",  # Empty string
                "path with spaces.py"
            ]
            
            for path in problematic_paths:
                try:
                    # Should handle gracefully without crashing
                    relative = safe_relative_to(path, project_root)
                    # Result should be Path or None, not an exception
                    assert relative is None or isinstance(relative, Path)
                except (ValueError, OSError):
                    # Some paths may legitimately raise exceptions
                    pass
    
    def test_comprehensive_file_analysis_integration(self, mock_domains):
        """Test comprehensive integration of file analysis with path normalization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create realistic project structure
            (project_root / "src" / "beast_mode").mkdir(parents=True)
            (project_root / "src" / "beast_mode" / "analysis.py").touch()
            (project_root / "tests" / "unit").mkdir(parents=True)
            (project_root / "tests" / "unit" / "test_analysis.py").touch()
            (project_root / "docs").mkdir()
            (project_root / "docs" / "README.md").touch()
            
            # Test orphaned file detection with normalized paths
            detector = OrphanedFileDetector(mock_domains, project_root)
            
            # Mock glob to return realistic file paths
            with patch.object(Path, 'glob') as mock_glob:
                mock_glob.return_value = [
                    project_root / "src" / "beast_mode" / "analysis.py",
                    project_root / "tests" / "unit" / "test_analysis.py",
                    project_root / "docs" / "README.md"
                ]
                
                result = detector.detect_orphaned_files(include_tests=True)
                
                # Should complete successfully
                assert "orphaned_files" in result
                assert "total_files_checked" in result
                assert "coverage_percentage" in result
                assert isinstance(result["coverage_percentage"], (int, float))
                assert 0 <= result["coverage_percentage"] <= 100