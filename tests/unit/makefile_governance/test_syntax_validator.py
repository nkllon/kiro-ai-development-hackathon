"""
Unit tests for MakefileSyntaxValidator.

Tests GNU Make syntax validation, embedded Python code validation,
and automatic repair functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.makefile_governance.core.syntax_validator import (
    MakefileSyntaxValidator,
    SyntaxError,
    SyntaxErrorType,
    ValidationResult
)
from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleCapability


class TestMakefileSyntaxValidator:
    """Test suite for MakefileSyntaxValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create a MakefileSyntaxValidator instance."""
        return MakefileSyntaxValidator()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_module_initialization(self, validator):
        """Test that the validator initializes correctly."""
        assert validator.module_id == "makefile_syntax_validator"
        assert isinstance(validator.get_capabilities(), list)
        assert ModuleCapability.VALIDATION in validator.get_capabilities()
        assert ModuleCapability.DATA_PROCESSING in validator.get_capabilities()
        assert ModuleCapability.CORE_FUNCTIONALITY in validator.get_capabilities()
    
    def test_get_module_info(self, validator):
        """Test module info retrieval."""
        info = validator.get_module_info()
        
        assert info["module_id"] == "makefile_syntax_validator"
        assert info["name"] == "Makefile Syntax Validator"
        assert info["version"] == "1.0.0"
        assert "capabilities" in info
        assert "statistics" in info
        assert "validations_performed" in info["statistics"]
        assert "repairs_performed" in info["statistics"]
        assert "errors_detected" in info["statistics"]
    
    def test_get_health_status_healthy(self, validator):
        """Test health status when validator is healthy."""
        health = validator.get_health_status()
        
        assert health.module_id == "makefile_syntax_validator"
        assert health.status == ModuleStatus.HEALTHY
        assert health.health_score == 1.0
        assert health.error_count == 0
    
    def test_get_health_status_with_errors(self, validator):
        """Test health status when validator has detected errors."""
        # Simulate some validation activity with errors
        validator._validation_count = 10
        validator._error_count = 2  # 20% error rate
        
        health = validator.get_health_status()
        
        assert health.status == ModuleStatus.WARNING
        assert health.health_score == 0.7
        assert health.error_count == 2
        assert len(health.issues) > 0
        assert "Detected 2 syntax errors" in health.issues[0]
    
    def test_graceful_degradation(self, validator):
        """Test graceful degradation functionality."""
        result = validator.graceful_degradation()
        
        assert result.success is True
        assert ModuleCapability.DATA_PROCESSING in result.degraded_capabilities
        assert ModuleCapability.VALIDATION in result.remaining_capabilities
        assert ModuleCapability.CORE_FUNCTIONALITY in result.remaining_capabilities
        assert result.error_message is None
    
    def test_validate_nonexistent_file(self, validator, temp_dir):
        """Test validation of non-existent makefile."""
        nonexistent_file = temp_dir / "nonexistent.mk"
        
        result = validator.validate_makefile(nonexistent_file)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].error_type == SyntaxErrorType.MALFORMED_TARGET
        assert "Makefile not found" in result.errors[0].message
    
    def test_validate_valid_makefile(self, validator, temp_dir):
        """Test validation of a valid makefile."""
        makefile_content = """# Valid Makefile
.PHONY: help clean test

PYTHON_VERSION := 3.9
PROJECT_NAME := test-project

help: ## Show help
\t@echo "Available targets:"
\t@echo "  help  - Show this help"
\t@echo "  clean - Clean build artifacts"

clean: ## Clean build artifacts
\t@echo "Cleaning..."
\trm -rf __pycache__/

test: ## Run tests
\t@echo "Running tests..."
\tpython -m pytest
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = validator.validate_makefile(makefile_path)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_validate_makefile_with_missing_separator(self, validator, temp_dir):
        """Test validation of makefile with missing separator error."""
        makefile_content = """# Makefile with missing separator
help:
@echo "This should have a tab"
echo "This line is missing tab separator"

clean:
\t@echo "This is correct"
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = validator.validate_makefile(makefile_path)
        
        assert result.is_valid is False
        assert len(result.errors) >= 1
        
        # Find the missing separator error
        missing_sep_errors = [e for e in result.errors if e.error_type == SyntaxErrorType.MISSING_SEPARATOR]
        assert len(missing_sep_errors) >= 1
        
        error = missing_sep_errors[0]
        assert "Missing separator" in error.message
        assert error.suggested_fix is not None
        assert error.suggested_fix.startswith('\t')
    
    def test_validate_makefile_with_invalid_recipe(self, validator, temp_dir):
        """Test validation of makefile with invalid recipe (spaces instead of tabs)."""
        makefile_content = """# Makefile with space-indented recipes
help:
    @echo "This uses spaces instead of tabs"
    echo "Another space-indented line"

clean:
\t@echo "This is correct with tab"
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = validator.validate_makefile(makefile_path)
        
        assert result.is_valid is False
        assert len(result.errors) >= 1
        
        # Find the invalid recipe errors
        recipe_errors = [e for e in result.errors if e.error_type == SyntaxErrorType.INVALID_RECIPE]
        assert len(recipe_errors) >= 1
        
        error = recipe_errors[0]
        assert "Recipe should start with tab" in error.message
        assert error.suggested_fix is not None
        assert '\t' in error.suggested_fix
    
    def test_validate_makefile_with_invalid_python_code(self, validator, temp_dir):
        """Test validation of makefile with invalid embedded Python code."""
        makefile_content = """# Makefile with invalid Python code
validate:
\tpython3 -c "
import sys
print('Hello World'
# Missing closing parenthesis - syntax error
"

test:
\tpython -c "print('Valid Python code')"
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = validator.validate_makefile(makefile_path)
        
        assert result.is_valid is False
        assert len(result.errors) >= 1
        
        # Find the Python syntax error
        python_errors = [e for e in result.errors if e.error_type == SyntaxErrorType.INVALID_PYTHON_CODE]
        assert len(python_errors) >= 1
        
        error = python_errors[0]
        assert "Invalid Python syntax" in error.message
    
    def test_validate_makefile_with_missing_phony_warnings(self, validator, temp_dir):
        """Test validation generates warnings for missing PHONY declarations."""
        makefile_content = """# Makefile missing PHONY declarations
help:
\t@echo "Show help"

clean:
\t@echo "Clean up"

test:
\t@echo "Run tests"

# Only help is declared as PHONY
.PHONY: help
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = validator.validate_makefile(makefile_path)
        
        assert result.is_valid is True  # No errors, just warnings
        assert len(result.warnings) >= 2  # clean and test should have warnings
        
        # Check for missing PHONY warnings
        phony_warnings = [w for w in result.warnings if w.error_type == SyntaxErrorType.MISSING_PHONY]
        assert len(phony_warnings) >= 2
        
        warning_targets = [w.suggested_fix for w in phony_warnings]
        assert any("clean" in fix for fix in warning_targets)
        assert any("test" in fix for fix in warning_targets)
    
    def test_repair_makefile_creates_backup(self, validator, temp_dir):
        """Test that repair creates a backup file."""
        makefile_content = """# Makefile with errors
help:
@echo "Missing tab"
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        with patch.object(validator, '_create_backup') as mock_backup:
            mock_backup.return_value = temp_dir / "Makefile.backup_test"
            
            result = validator.repair_makefile(makefile_path, create_backup=True)
            
            mock_backup.assert_called_once_with(makefile_path)
            assert result.backup_path is not None
    
    def test_repair_makefile_fixes_missing_separator(self, validator, temp_dir):
        """Test that repair fixes missing separator errors."""
        makefile_content = """# Makefile with missing separator
help:
@echo "Missing tab"
echo "Another missing tab"

clean:
\t@echo "This is correct"
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = validator.repair_makefile(makefile_path, create_backup=False)
        
        assert result.repaired_content is not None
        assert '\t@echo "Missing tab"' in result.repaired_content
        assert '\techo "Another missing tab"' in result.repaired_content
        
        # Verify the repaired content is valid
        repaired_validation = validator._validate_content(result.repaired_content)
        missing_sep_errors = [e for e in repaired_validation.errors 
                             if e.error_type == SyntaxErrorType.MISSING_SEPARATOR]
        assert len(missing_sep_errors) == 0
    
    def test_repair_makefile_fixes_invalid_recipe(self, validator, temp_dir):
        """Test that repair fixes invalid recipe spacing."""
        makefile_content = """# Makefile with space-indented recipes
help:
    @echo "Uses spaces"
    echo "More spaces"

clean:
\t@echo "Correct tab"
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = validator.repair_makefile(makefile_path, create_backup=False)
        
        assert result.repaired_content is not None
        
        # Check that spaces were converted to tabs
        lines = result.repaired_content.split('\n')
        recipe_lines = [line for line in lines if line.startswith('\t') and '@echo' in line]
        assert len(recipe_lines) >= 2  # Should have fixed the space-indented lines
    
    def test_repair_already_valid_makefile(self, validator, temp_dir):
        """Test repair of an already valid makefile."""
        makefile_content = """# Valid Makefile
.PHONY: help

help:
\t@echo "Show help"
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = validator.repair_makefile(makefile_path, create_backup=False)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.repaired_content is None  # No repairs needed
    
    def test_should_be_phony_detection(self, validator):
        """Test detection of targets that should be PHONY."""
        assert validator._should_be_phony("help") is True
        assert validator._should_be_phony("clean") is True
        assert validator._should_be_phony("test") is True
        assert validator._should_be_phony("install") is True
        assert validator._should_be_phony("build-docker") is True
        assert validator._should_be_phony("run-tests") is True
        
        # These should not be PHONY
        assert validator._should_be_phony("main.o") is False
        assert validator._should_be_phony("program") is False
        assert validator._should_be_phony("lib.a") is False
    
    def test_create_backup(self, validator, temp_dir):
        """Test backup file creation."""
        makefile_content = "# Test makefile\nhelp:\n\t@echo 'help'"
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        backup_path = validator._create_backup(makefile_path)
        
        assert backup_path.exists()
        assert backup_path.name.startswith("Makefile.backup_")
        assert backup_path.read_text() == makefile_content
    
    def test_validate_python_code_valid(self, validator):
        """Test validation of valid Python code."""
        content = '''test:
\tpython3 -c "import sys; print('Hello World')"
\tpython -c "x = 1 + 2; print(x)"
'''
        
        errors = validator._validate_python_code(content)
        assert len(errors) == 0
    
    def test_validate_python_code_invalid(self, validator):
        """Test validation of invalid Python code."""
        content = '''test:
\tpython3 -c "import sys; print('Hello World'"
\tpython -c "x = 1 + ; print(x)"
'''
        
        errors = validator._validate_python_code(content)
        assert len(errors) >= 1
        
        for error in errors:
            assert error.error_type == SyntaxErrorType.INVALID_PYTHON_CODE
            assert "Invalid Python syntax" in error.message
    
    def test_validation_statistics_tracking(self, validator, temp_dir):
        """Test that validation statistics are properly tracked."""
        # Create a makefile with errors
        makefile_content = """help:
@echo "Missing tab"
"""
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        initial_validation_count = validator._validation_count
        initial_error_count = validator._error_count
        
        # Perform validation
        result = validator.validate_makefile(makefile_path)
        
        # Check statistics were updated
        assert validator._validation_count == initial_validation_count + 1
        assert validator._error_count > initial_error_count
        
        # Perform repair
        initial_repair_count = validator._repair_count
        validator.repair_makefile(makefile_path, create_backup=False)
        
        assert validator._repair_count == initial_repair_count + 1
    
    def test_trace_operation_integration(self, validator, temp_dir):
        """Test that operations are properly traced."""
        makefile_content = "help:\n\t@echo 'help'"
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        # Mock the trace_operation context manager
        with patch.object(validator, 'trace_operation') as mock_trace:
            mock_context = MagicMock()
            mock_trace.return_value.__enter__ = Mock(return_value=mock_context)
            mock_trace.return_value.__exit__ = Mock(return_value=None)
            
            result = validator.validate_makefile(makefile_path)
            
            # Verify trace_operation was called
            mock_trace.assert_called_once_with("validate_makefile", file_path=str(makefile_path))
            
            # Verify output_result was set
            assert mock_context.output_result is not None
    
    def test_complex_makefile_validation(self, validator, temp_dir):
        """Test validation of a complex makefile with multiple error types."""
        makefile_content = """# Complex Makefile with multiple issues
PYTHON_VERSION = 3.9
PROJECT_NAME := test-project

# Missing PHONY declarations
help:
\t@echo "Available targets:"

clean:
    @echo "Cleaning..."  # Space instead of tab
    rm -rf __pycache__/

test:
\t@echo "Running tests..."
\tpython3 -c "
import sys
print('Running tests'
# Missing closing parenthesis
"

build: help  # Valid dependency
\t@echo "Building project..."

# Invalid target line
invalid-target-line-without-colon
\t@echo "This should not work"
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = validator.validate_makefile(makefile_path)
        
        assert result.is_valid is False
        assert len(result.errors) >= 3  # Should have multiple types of errors
        
        # Check for different error types
        error_types = [error.error_type for error in result.errors]
        assert SyntaxErrorType.INVALID_RECIPE in error_types
        assert SyntaxErrorType.INVALID_PYTHON_CODE in error_types
        
        # Check for warnings about missing PHONY
        assert len(result.warnings) >= 2  # help, clean, test should generate warnings
    
    @pytest.mark.parametrize("target_name,should_be_phony", [
        ("help", True),
        ("clean", True),
        ("test", True),
        ("install", True),
        ("deploy", True),
        ("build", True),
        ("run", True),
        ("start", True),
        ("stop", True),
        ("check", True),
        ("lint", True),
        ("format", True),
        ("validate", True),
        ("setup", True),
        ("init", True),
        ("main.o", False),
        ("program", False),
        ("lib.a", False),
        ("config.json", False),
        ("data.txt", False),
    ])
    def test_phony_detection_parametrized(self, validator, target_name, should_be_phony):
        """Parametrized test for PHONY target detection."""
        assert validator._should_be_phony(target_name) == should_be_phony