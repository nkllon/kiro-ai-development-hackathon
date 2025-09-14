"""
Test suite for Hackathon Demo Framework validation components.

Tests the code quality assessment engine and installation validator.
"""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hackathon_demo_framework.validation.code_quality_validator import (
    CodeQualityAssessmentEngine,
    CodeQualityMetric,
    CodeQualityIssue,
    CodeQualityReport
)
from hackathon_demo_framework.validation.installation_validator import (
    InstallationSetupValidator,
    InstallationIssueType,
    InstallationIssue,
    InstallationReport
)

class TestCodeQualityAssessmentEngine(ReflectiveModule):
    """Test suite for the code quality assessment engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.engine = CodeQualityAssessmentEngine(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_engine_initialization(self):
        """Test code quality engine initialization."""
        assert self.engine.project_path == self.temp_dir
        assert "complexity_max" in self.engine.thresholds
        assert len(self.engine.source_patterns) > 0
        assert len(self.engine.exclude_patterns) > 0
    
    def test_code_quality_issue_creation(self):
        """Test code quality issue data structure."""
        issue = CodeQualityIssue(
            file_path="test.py",
            line_number=10,
            issue_type=CodeQualityMetric.COMPLEXITY,
            severity="major",
            message="Function too complex",
            suggestion="Break down function"
        )
        
        assert issue.file_path == "test.py"
        assert issue.line_number == 10
        assert issue.issue_type == CodeQualityMetric.COMPLEXITY
        assert issue.severity == "major"
        assert issue.message == "Function too complex"
        assert issue.suggestion == "Break down function"
    
    def test_empty_project_assessment(self):
        """Test assessment of empty project."""
        report = self.engine.assess_code_quality()
        
        # Should handle empty project gracefully
        assert isinstance(report, CodeQualityReport)
        assert report.files_analyzed == 0
        assert report.lines_of_code == 0
        assert report.overall_score == 0.0  # No files to analyze
    
    def test_simple_python_file_assessment(self):
        """Test assessment of simple Python file."""
        # Create a simple Python file in the root (matches *.py pattern)
        test_file = self.temp_dir / "simple_module.py"  # Avoid 'test_' prefix
        
        test_code = '''"""
Simple test module.
"""

def hello_world():
    """Say hello to the world."""
    return "Hello, World!"

class TestClass(ReflectiveModule):
    """A simple test class."""
    
    def __init__(self):
        self.module_id = self.__class__.__name__
        self.health_status = "healthy"
        self.registry_metadata = {}
        """Initialize the test class."""
        self.value = 42
    
    def get_value(self):
        """Get the stored value."""
        return self.value
'''
        
        test_file.write_text(test_code)
        
        report = self.engine.assess_code_quality()
        
        # Should analyze the file successfully
        assert report.files_analyzed == 1
        assert report.lines_of_code > 0
        assert report.overall_score > 0
        assert report.documentation_score > 80  # Well documented
        assert report.complexity_score > 80  # Simple functions
    
    def test_complex_code_detection(self):
        """Test detection of complex code patterns."""
        # Create a complex Python file in the root
        test_file = self.temp_dir / "complex_module.py"
        
        complex_code = '''
def extremely_complex_function(a, b, c, d, e, f, g, h, i, j, k, l):
    # This function has very high cyclomatic complexity
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            if g > 0:
                                if h > 0:
                                    if i > 0:
                                        if j > 0:
                                            if k > 0:
                                                if l > 0:
                                                    for x in range(10):
                                                        if x % 2 == 0:
                                                            if x > 5:
                                                                while x < 20:
                                                                    try:
                                                                        if x % 3 == 0:
                                                                            return x
                                                                        elif x % 4 == 0:
                                                                            return x * 2
                                                                        else:
                                                                            x += 1
                                                                    except:
                                                                        return 0
                                                            else:
                                                                return x
                                                        else:
                                                            return 0
                                                else:
                                                    return 0
                                            else:
                                                return 0
                                        else:
                                            return 0
                                    else:
                                        return 0
                                else:
                                    return 0
                            else:
                                return 0
                        else:
                            return 0
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0
        else:
            return 0
    else:
        return 0

def another_complex_function():
    # Another complex function to lower the average
    for i in range(100):
        if i % 2 == 0:
            if i % 3 == 0:
                if i % 5 == 0:
                    if i % 7 == 0:
                        if i % 11 == 0:
                            return i
                        else:
                            continue
                    else:
                        continue
                else:
                    continue
            else:
                continue
        else:
            continue
    return 0
'''
        
        test_file.write_text(complex_code)
        
        report = self.engine.assess_code_quality()
        
        # Should detect complexity issues
        assert report.files_analyzed == 1
        assert report.complexity_score < 80  # Should detect high complexity
        assert report.total_issues > 0
        
        # Should have complexity-related issues
        complexity_issues = [i for i in report.issues if i.issue_type == CodeQualityMetric.COMPLEXITY]
        assert len(complexity_issues) > 0
    
    def test_documentation_analysis(self):
        """Test documentation coverage analysis."""
        # Create file with mixed documentation in the root
        test_file = self.temp_dir / "doc_module.py"  # Avoid 'test_' prefix
        
        mixed_doc_code = '''
def documented_function():
    """This function is well documented."""
    return True

def undocumented_function():
    return False

class DocumentedClass(ReflectiveModule):
    """This class has documentation."""
    
    def documented_method(self):
        """This method is documented."""
        pass
    
    def undocumented_method(self):
        pass

class UndocumentedClass(ReflectiveModule):
    def some_method(self):
        pass
'''
        
        test_file.write_text(mixed_doc_code)
        
        report = self.engine.assess_code_quality()
        
        # Should detect documentation issues
        assert report.files_analyzed == 1
        assert 40 <= report.documentation_score <= 80  # Mixed documentation
        
        # Should have documentation-related issues
        doc_issues = [i for i in report.issues if i.issue_type == CodeQualityMetric.DOCUMENTATION]
        assert len(doc_issues) > 0
    
    def test_security_issue_detection(self):
        """Test detection of security issues."""
        # Create file with security issues in the root
        test_file = self.temp_dir / "security_module.py"  # Avoid 'test_' prefix
        
        insecure_code = '''
import os
import subprocess

def dangerous_function(user_input):
    # Security issues
    result = eval(user_input)
    os.system(f"echo {user_input}")
    subprocess.call(user_input, shell=True)
    
    # Hardcoded secrets
    api_key = "sk-1234567890abcdef"
    password = "super_secret_password"
    
    return result
'''
        
        test_file.write_text(insecure_code)
        
        report = self.engine.assess_code_quality()
        
        # Should detect security issues
        assert report.files_analyzed == 1
        assert report.security_score < 80  # Should detect security problems
        assert report.critical_issues > 0  # Hardcoded secrets are critical
        
        # Should have security-related issues
        security_issues = [i for i in report.issues if i.issue_type == CodeQualityMetric.SECURITY]
        assert len(security_issues) > 0
    
    def test_validation_with_thresholds(self):
        """Test code quality validation against thresholds."""
        # Create a high-quality file in the root
        test_file = self.temp_dir / "quality_module.py"  # Avoid 'test_' prefix
        
        quality_code = '''"""
High-quality test module.
"""

def simple_function(value: int) -> str:
    """
    Convert integer to string.
    
    Args:
        value: Integer value to convert
        
    Returns:
        String representation of the value
    """
    return str(value)

class WellDesignedClass(ReflectiveModule):
    """A well-designed class with proper documentation."""
    
    def __init__(self, initial_value: int = 0):
        self.module_id = self.__class__.__name__
        self.health_status = "healthy"
        self.registry_metadata = {}
        """
        Initialize the class.
        
        Args:
            initial_value: Initial value to store
        """
        self._value = initial_value
    
    def get_value(self) -> int:
        """Get the stored value."""
        return self._value
    
    def set_value(self, new_value: int) -> None:
        """Set a new value."""
        self._value = new_value
'''
        
        test_file.write_text(quality_code)
        
        # Test validation with high threshold
        validation_result = self.engine.validate_code_quality(min_score=80.0)
        
        assert validation_result.score > 80.0
        assert validation_result.is_valid
        assert len(validation_result.issues) == 0
    
    def test_improvement_plan_generation(self):
        """Test generation of improvement plans."""
        # Create a report with various issues
        issues = [
            CodeQualityIssue("test.py", 1, CodeQualityMetric.COMPLEXITY, "critical", "Critical complexity"),
            CodeQualityIssue("test.py", 2, CodeQualityMetric.DOCUMENTATION, "major", "Missing docs"),
            CodeQualityIssue("test.py", 3, CodeQualityMetric.STYLE, "minor", "Style issue")
        ]
        
        report = CodeQualityReport(
            overall_score=60.0,
            complexity_score=50.0,
            maintainability_score=70.0,
            documentation_score=60.0,
            style_score=70.0,
            security_score=90.0,
            performance_score=80.0,
            total_issues=3,
            critical_issues=1,
            major_issues=1,
            minor_issues=1,
            issues=issues,
            recommendations=[],
            files_analyzed=1,
            lines_of_code=100
        )
        
        improvement_plan = self.engine.generate_quality_improvement_plan(report)
        
        assert len(improvement_plan) > 0
        assert any("CRITICAL" in step for step in improvement_plan)
        assert any("complexity" in step.lower() for step in improvement_plan)
        assert any("documentation" in step.lower() for step in improvement_plan)

class TestInstallationSetupValidator(ReflectiveModule):
    """Test suite for the installation setup validator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.validator = InstallationSetupValidator(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validator_initialization(self):
        """Test installation validator initialization."""
        assert self.validator.project_path == self.temp_dir
        assert len(self.validator.config_files) > 0
        assert len(self.validator.doc_files) > 0
        assert len(self.validator.required_sections) > 0
    
    def test_installation_issue_creation(self):
        """Test installation issue data structure."""
        issue = InstallationIssue(
            issue_type=InstallationIssueType.MISSING_REQUIREMENTS,
            severity="critical",
            message="No requirements file found",
            file_path="requirements.txt",
            suggestion="Add requirements.txt file"
        )
        
        assert issue.issue_type == InstallationIssueType.MISSING_REQUIREMENTS
        assert issue.severity == "critical"
        assert issue.message == "No requirements file found"
        assert issue.file_path == "requirements.txt"
        assert issue.suggestion == "Add requirements.txt file"
    
    def test_empty_project_validation(self):
        """Test validation of empty project."""
        report = self.validator.validate_installation_setup()
        
        # Should detect missing files
        assert isinstance(report, InstallationReport)
        assert report.overall_score < 50  # Should be low due to missing files
        assert report.critical_issues > 0  # Missing requirements and README
    
    def test_requirements_txt_validation(self):
        """Test validation of requirements.txt file."""
        # Create a good requirements.txt
        requirements_file = self.temp_dir / "requirements.txt"
        requirements_content = '''# Project dependencies
flask==2.0.1
requests>=2.25.0
pytest~=6.2.0
'''
        requirements_file.write_text(requirements_content)
        
        report = self.validator.validate_installation_setup()
        
        # Should improve requirements score
        assert report.requirements_score > 50
        
        # Create a bad requirements.txt
        bad_requirements = '''flask
requests
invalid-package-name!@#
'''
        requirements_file.write_text(bad_requirements)
        
        report = self.validator.validate_installation_setup()
        
        # Should detect issues
        req_issues = [i for i in report.issues if i.issue_type == InstallationIssueType.DEPENDENCY_CONFLICT]
        assert len(req_issues) > 0
    
    def test_readme_validation(self):
        """Test validation of README file."""
        # Create a comprehensive README
        readme_file = self.temp_dir / "README.md"
        readme_content = '''# Test Project

This is a test project for validation.

## Installation

To install this project:

```bash
pip install -r requirements.txt
```

## Setup

1. Clone the repository
2. Install dependencies
3. Run the application

## Usage

Run the application with:

```bash
python main.py
```

## Requirements

- Python 3.8+
- pip

## Getting Started

Follow the installation steps above to get started.
'''
        readme_file.write_text(readme_content)
        
        report = self.validator.validate_installation_setup()
        
        # Should improve documentation score
        assert report.documentation_score > 80
        assert report.setup_score > 70
        
        # Should find required sections
        setup_issues = [i for i in report.issues if i.issue_type == InstallationIssueType.SETUP_INSTRUCTIONS]
        doc_issues = [i for i in report.issues if i.issue_type == InstallationIssueType.DOCUMENTATION]
        
        # Should have fewer issues with good README
        assert len(setup_issues) < 2
        assert len(doc_issues) < 2
    
    def test_pyproject_toml_validation(self):
        """Test validation of pyproject.toml file."""
        # Create a valid pyproject.toml
        pyproject_file = self.temp_dir / "pyproject.toml"
        pyproject_content = '''[project]
name = "test-project"
version = "1.0.0"
description = "A test project"
dependencies = [
    "flask>=2.0.0",
    "requests>=2.25.0"
]

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
'''
        pyproject_file.write_text(pyproject_content)
        
        report = self.validator.validate_installation_setup()
        
        # Should improve requirements score
        assert report.requirements_score > 70
    
    def test_installation_guide_generation(self):
        """Test generation of installation guide."""
        # Create some project files
        (self.temp_dir / "requirements.txt").write_text("flask==2.0.1\nrequests>=2.25.0")
        (self.temp_dir / "main.py").write_text("print('Hello, World!')")
        
        guide = self.validator.generate_installation_guide()
        
        # Should generate comprehensive guide
        assert "# Installation Guide" in guide
        assert "Prerequisites" in guide
        assert "Installation Steps" in guide
        assert "requirements.txt" in guide
        assert "Virtual Environment" in guide
        assert "Troubleshooting" in guide
        assert "```bash" in guide  # Should have code blocks
    
    def test_dependency_validation(self):
        """Test dependency conflict validation."""
        report = self.validator.validate_installation_setup()
        
        # Should have good dependency score with no conflicts
        dependency_issues = [i for i in report.issues if i.issue_type == InstallationIssueType.DEPENDENCY_CONFLICT]
        assert len(dependency_issues) == 0
        
        # Create a requirements file with conflicts to test detection
        (self.temp_dir / "requirements.txt").write_text("package-a==1.0\npackage-a>=2.0")
        
        report = self.validator.validate_installation_setup()
        
        # Should detect dependency conflicts
        dependency_issues = [i for i in report.issues if i.issue_type == InstallationIssueType.DEPENDENCY_CONFLICT]
        assert len(dependency_issues) > 0
    
    def test_comprehensive_project_validation(self):
        """Test validation of a well-configured project."""
        # Create a complete project structure
        (self.temp_dir / "requirements.txt").write_text('''
flask==2.0.1
requests>=2.25.0
pytest~=6.2.0
''')
        
        (self.temp_dir / "README.md").write_text('''
# Test Project

## Installation

```bash
pip install -r requirements.txt
```

## Setup

1. Clone repository
2. Install dependencies
3. Configure environment

## Usage

Run with: `python main.py`

## Requirements

- Python 3.8+
- pip
''')
        
        (self.temp_dir / "main.py").write_text("print('Hello, World!')")
        
        report = self.validator.validate_installation_setup()
        
        # Should have good overall score
        assert report.overall_score > 70
        assert report.requirements_score > 80
        assert report.documentation_score > 80
        assert report.setup_score > 70
        
        # Should have minimal critical issues
        assert report.critical_issues <= 1  # May have environment test issues
    
    def test_reliability_validation(self):
        """Test installation reliability validation."""
        # Create minimal project
        (self.temp_dir / "requirements.txt").write_text("requests>=2.25.0")
        (self.temp_dir / "README.md").write_text("# Test\n\n## Installation\n\n```bash\npip install -r requirements.txt\n```")
        
        # Test with minimal attempts for speed
        with patch.object(self.validator, '_test_single_installation') as mock_test:
            # Mock successful installations
            mock_test.return_value = {"success": True, "issues": []}
            
            result = self.validator.validate_installation_reliability(num_tests=2)
            
            assert result.score == 100.0  # All attempts successful
            assert result.is_valid
            assert len(result.issues) == 0
            
            # Mock failed installations
            mock_test.return_value = {"success": False, "issues": ["Installation failed"]}
            
            result = self.validator.validate_installation_reliability(num_tests=2)
            
            assert result.score == 0.0  # All attempts failed
            assert not result.is_valid
            assert len(result.issues) > 0

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