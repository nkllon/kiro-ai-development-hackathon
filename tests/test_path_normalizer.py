"""
Unit tests for PathNormalizer utility class.

Tests the path normalization functionality including:
- Path normalization and resolution
- Relative path handling
- Path validation and safety checks
- Common base directory detection
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

from src.beast_mode.utils.path_normalizer import (
    PathNormalizer,
    PathValidator,
    normalize_path,
    ensure_relative_to,
    safe_relative_to
)


class TestPathNormalizer:
    """Test suite for PathNormalizer class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def sample_paths(self, temp_dir):
        """Create sample paths for testing."""
        # Create some test files and directories
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "main.py").touch()
        (temp_dir / "tests").mkdir()
        (temp_dir / "tests" / "test_main.py").touch()
        (temp_dir / "docs").mkdir()
        (temp_dir / "docs" / "readme.md").touch()
        
        return {
            "base": temp_dir,
            "src_file": temp_dir / "src" / "main.py",
            "test_file": temp_dir / "tests" / "test_main.py",
            "doc_file": temp_dir / "docs" / "readme.md"
        }
    
    def test_normalize_path_relative(self, temp_dir):
        """Test normalization of relative paths."""
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            result = PathNormalizer.normalize_path("src/main.py")
            expected = temp_dir / "src" / "main.py"
            assert result == expected.resolve()
    
    def test_normalize_path_absolute(self, temp_dir):
        """Test normalization of absolute paths."""
        absolute_path = temp_dir / "src" / "main.py"
        result = PathNormalizer.normalize_path(str(absolute_path))
        assert result == absolute_path.resolve()
    
    def test_normalize_path_with_path_object(self, temp_dir):
        """Test normalization with Path objects."""
        path_obj = Path("src/main.py")
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            result = PathNormalizer.normalize_path(path_obj)
            expected = temp_dir / "src" / "main.py"
            assert result == expected.resolve()
    
    def test_ensure_relative_to_success(self, sample_paths):
        """Test successful relative path conversion."""
        base = sample_paths["base"]
        src_file = sample_paths["src_file"]
        
        result = PathNormalizer.ensure_relative_to(src_file, base)
        assert result == Path("src") / "main.py"
    
    def test_ensure_relative_to_already_relative(self, sample_paths):
        """Test ensure_relative_to with already relative path."""
        base = sample_paths["base"]
        relative_path = "src/main.py"
        
        with patch('pathlib.Path.cwd', return_value=base):
            result = PathNormalizer.ensure_relative_to(relative_path, base)
            assert result == Path("src") / "main.py"
    
    def test_ensure_relative_to_failure(self, temp_dir):
        """Test ensure_relative_to with incompatible paths."""
        with tempfile.TemporaryDirectory() as other_temp:
            other_path = Path(other_temp) / "file.py"
            
            with pytest.raises(ValueError, match="cannot be made relative"):
                PathNormalizer.ensure_relative_to(other_path, temp_dir)
    
    def test_ensure_relative_to_relative_path_not_under_base(self, temp_dir):
        """Test ensure_relative_to with relative path that's already relative."""
        relative_path = "src/main.py"
        result = PathNormalizer.ensure_relative_to(relative_path, temp_dir)
        assert result == Path("src/main.py")
    
    def test_safe_relative_to_success(self, sample_paths):
        """Test safe_relative_to with valid paths."""
        base = sample_paths["base"]
        src_file = sample_paths["src_file"]
        
        result = PathNormalizer.safe_relative_to(src_file, base)
        assert result == Path("src") / "main.py"
    
    def test_safe_relative_to_failure(self, temp_dir):
        """Test safe_relative_to with incompatible paths."""
        with tempfile.TemporaryDirectory() as other_temp:
            other_path = Path(other_temp) / "file.py"
            
            result = PathNormalizer.safe_relative_to(other_path, temp_dir)
            assert result is None
    
    def test_validate_path_consistency_success(self, sample_paths):
        """Test path consistency validation with valid paths."""
        base = sample_paths["base"]
        paths = [
            "src/main.py",
            "tests/test_main.py",
            "docs/readme.md"
        ]
        
        with patch('pathlib.Path.cwd', return_value=base):
            result = PathNormalizer.validate_path_consistency(paths, base)
            assert result is True
    
    def test_validate_path_consistency_without_base(self, sample_paths):
        """Test path consistency validation without base."""
        paths = [
            str(sample_paths["src_file"]),
            str(sample_paths["test_file"]),
            str(sample_paths["doc_file"])
        ]
        
        result = PathNormalizer.validate_path_consistency(paths)
        assert result is True
    
    def test_validate_path_consistency_duplicates(self, temp_dir):
        """Test path consistency validation with duplicate paths."""
        paths = [
            "src/main.py",
            "./src/main.py",  # Same file, different representation
        ]
        
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            result = PathNormalizer.validate_path_consistency(paths)
            assert result is False
    
    def test_resolve_path_conflict_keep_relative(self, sample_paths):
        """Test path conflict resolution keeping relative path."""
        base = sample_paths["base"]
        relative_path = "src/main.py"
        
        with patch('pathlib.Path.cwd', return_value=base):
            result = PathNormalizer.resolve_path_conflict(relative_path, base)
            assert result == Path("src/main.py")
            assert not result.is_absolute()
    
    def test_resolve_path_conflict_make_relative(self, sample_paths):
        """Test path conflict resolution making absolute path relative."""
        base = sample_paths["base"]
        absolute_path = sample_paths["src_file"]
        
        result = PathNormalizer.resolve_path_conflict(absolute_path, base)
        assert result == Path("src") / "main.py"
        assert not result.is_absolute()
    
    def test_resolve_path_conflict_keep_absolute(self, temp_dir):
        """Test path conflict resolution keeping absolute path when necessary."""
        with tempfile.TemporaryDirectory() as other_temp:
            other_path = Path(other_temp) / "file.py"
            
            result = PathNormalizer.resolve_path_conflict(other_path, temp_dir)
            assert result.is_absolute()
    
    def test_get_common_base_success(self, sample_paths):
        """Test finding common base directory."""
        paths = [
            sample_paths["src_file"],
            sample_paths["test_file"],
            sample_paths["doc_file"]
        ]
        
        result = PathNormalizer.get_common_base(paths)
        # Use resolve() to handle symlinks consistently
        assert result.resolve() == sample_paths["base"].resolve()
    
    def test_get_common_base_no_common(self):
        """Test finding common base with no common directory."""
        with tempfile.TemporaryDirectory() as temp1, tempfile.TemporaryDirectory() as temp2:
            paths = [
                Path(temp1) / "file1.py",
                Path(temp2) / "file2.py"
            ]
            
            result = PathNormalizer.get_common_base(paths)
            # Should find root or a common ancestor
            assert result is not None
    
    def test_get_common_base_empty_list(self):
        """Test finding common base with empty path list."""
        result = PathNormalizer.get_common_base([])
        assert result is None
    
    def test_get_common_base_single_path(self, sample_paths):
        """Test finding common base with single path."""
        paths = [sample_paths["src_file"]]
        
        result = PathNormalizer.get_common_base(paths)
        # Use resolve() to handle symlinks consistently
        assert result.resolve() == sample_paths["src_file"].resolve()


class TestPathValidator:
    """Test suite for PathValidator class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_is_safe_path_valid(self, temp_dir):
        """Test safe path validation with valid path."""
        safe_path = temp_dir / "src" / "main.py"
        result = PathValidator.is_safe_path(safe_path, temp_dir)
        assert result is True
    
    def test_is_safe_path_relative_valid(self, temp_dir):
        """Test safe path validation with valid relative path."""
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            result = PathValidator.is_safe_path("src/main.py", temp_dir)
            assert result is True
    
    def test_is_safe_path_escape_attempt(self, temp_dir):
        """Test safe path validation with path escape attempt."""
        with tempfile.TemporaryDirectory() as other_temp:
            unsafe_path = Path(other_temp) / "file.py"
            result = PathValidator.is_safe_path(unsafe_path, temp_dir)
            assert result is False
    
    def test_validate_file_extension_valid(self):
        """Test file extension validation with valid extensions."""
        assert PathValidator.validate_file_extension("file.py", [".py", ".pyx"])
        assert PathValidator.validate_file_extension("file.py", ["py", "pyx"])
        assert PathValidator.validate_file_extension("FILE.PY", [".py"])  # Case insensitive
    
    def test_validate_file_extension_invalid(self):
        """Test file extension validation with invalid extensions."""
        assert not PathValidator.validate_file_extension("file.py", [".js", ".ts"])
        assert not PathValidator.validate_file_extension("file", [".py"])
    
    def test_validate_path_length_valid(self):
        """Test path length validation with valid length."""
        short_path = "src/main.py"
        assert PathValidator.validate_path_length(short_path, 260)
        assert PathValidator.validate_path_length(short_path, 20)
    
    def test_validate_path_length_invalid(self):
        """Test path length validation with invalid length."""
        long_path = "a" * 300
        assert not PathValidator.validate_path_length(long_path, 260)
        assert PathValidator.validate_path_length(long_path, 400)


class TestConvenienceFunctions:
    """Test suite for convenience functions."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_normalize_path_convenience(self, temp_dir):
        """Test normalize_path convenience function."""
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            result = normalize_path("src/main.py")
            expected = temp_dir / "src" / "main.py"
            assert result == expected.resolve()
    
    def test_ensure_relative_to_convenience(self, temp_dir):
        """Test ensure_relative_to convenience function."""
        absolute_path = temp_dir / "src" / "main.py"
        result = ensure_relative_to(absolute_path, temp_dir)
        assert result == Path("src") / "main.py"
    
    def test_safe_relative_to_convenience(self, temp_dir):
        """Test safe_relative_to convenience function."""
        absolute_path = temp_dir / "src" / "main.py"
        result = safe_relative_to(absolute_path, temp_dir)
        assert result == Path("src") / "main.py"
    
    def test_safe_relative_to_convenience_failure(self, temp_dir):
        """Test safe_relative_to convenience function with failure."""
        with tempfile.TemporaryDirectory() as other_temp:
            other_path = Path(other_temp) / "file.py"
            result = safe_relative_to(other_path, temp_dir)
            assert result is None


class TestPathNormalizerIntegration:
    """Integration tests for PathNormalizer with real file system scenarios."""
    
    @pytest.fixture
    def project_structure(self):
        """Create a realistic project structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create project structure
            (project_root / "src" / "beast_mode").mkdir(parents=True)
            (project_root / "src" / "beast_mode" / "__init__.py").touch()
            (project_root / "src" / "beast_mode" / "main.py").touch()
            (project_root / "tests").mkdir()
            (project_root / "tests" / "test_main.py").touch()
            (project_root / "docs").mkdir()
            (project_root / "docs" / "README.md").touch()
            
            yield project_root
    
    def test_real_project_path_handling(self, project_structure):
        """Test path handling with realistic project structure."""
        project_root = project_structure
        
        # Test various path representations
        paths_to_test = [
            "src/beast_mode/main.py",
            "./src/beast_mode/main.py",
            str(project_root / "src" / "beast_mode" / "main.py"),
            project_root / "src" / "beast_mode" / "main.py"
        ]
        
        # All should normalize to the same relative path
        expected_relative = Path("src") / "beast_mode" / "main.py"
        
        for path in paths_to_test:
            with patch('pathlib.Path.cwd', return_value=project_root):
                result = PathNormalizer.ensure_relative_to(path, project_root)
                assert result == expected_relative
    
    def test_mixed_path_types_consistency(self, project_structure):
        """Test consistency with mixed absolute and relative paths."""
        project_root = project_structure
        
        mixed_paths = [
            "src/beast_mode/main.py",  # Relative
            str(project_root / "tests" / "test_main.py"),  # Absolute string
            project_root / "docs" / "README.md"  # Absolute Path object
        ]
        
        # Should be able to validate consistency
        with patch('pathlib.Path.cwd', return_value=project_root):
            result = PathNormalizer.validate_path_consistency(mixed_paths, project_root)
            assert result is True
    
    def test_common_base_detection_realistic(self, project_structure):
        """Test common base detection with realistic paths."""
        project_root = project_structure
        
        paths = [
            project_root / "src" / "beast_mode" / "main.py",
            project_root / "tests" / "test_main.py",
            project_root / "docs" / "README.md"
        ]
        
        common_base = PathNormalizer.get_common_base(paths)
        # Use resolve() to handle symlinks consistently
        assert common_base.resolve() == project_root.resolve()
    
    def test_path_conflict_resolution_realistic(self, project_structure):
        """Test path conflict resolution with realistic scenarios."""
        project_root = project_structure
        
        # Test different conflict scenarios
        test_cases = [
            ("src/beast_mode/main.py", Path("src") / "beast_mode" / "main.py"),
            (str(project_root / "tests" / "test_main.py"), Path("tests") / "test_main.py"),
            (project_root / "docs" / "README.md", Path("docs") / "README.md")
        ]
        
        for input_path, expected_relative in test_cases:
            with patch('pathlib.Path.cwd', return_value=project_root):
                result = PathNormalizer.resolve_path_conflict(input_path, project_root)
                assert result == expected_relative
                assert not result.is_absolute()