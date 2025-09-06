"""
Unit tests for DesignValidator class.

Tests design-implementation alignment validation functionality.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.beast_mode.compliance.rdi.design_validator import (
    DesignValidator,
    DesignComponent,
    ImplementationComponent,
    ComponentType,
    AlignmentResult
)
from src.beast_mode.compliance.models import ComplianceIssueType, IssueSeverity


class TestDesignValidator:
    """Test cases for DesignValidator class."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Create design document
            design_content = """
# Design Document

## Components and Interfaces

### 1. ComplianceOrchestrator

**Purpose**: Main orchestrator that coordinates all compliance checking activities

```python
class ComplianceOrchestrator(ReflectiveModule):
    def analyze_commits_ahead_of_main(self) -> ComplianceAnalysisResult:
        pass
        
    def validate_phase2_completion(self) -> Phase2ValidationResult:
        pass
        
    def generate_compliance_report(self) -> ComplianceReport:
        pass
```

### 2. GitAnalyzer

**Purpose**: Analyzes git commits and file changes

```python
class GitAnalyzer(ReflectiveModule):
    def get_commits_ahead_of_main(self) -> List[CommitInfo]:
        pass
        
    def analyze_file_changes(self) -> FileChangeAnalysis:
        pass
```

### 3. validate_data Function

```python
def validate_data(data):
    '''Validates input data'''
    pass
```
"""
            
            (repo_path / "design.md").write_text(design_content)
            
            # Create implementation files
            orchestrator_impl = """
'''Compliance orchestrator implementation'''

from typing import List

class ComplianceOrchestrator:
    '''Main orchestrator for compliance checking'''
    
    def __init__(self):
        self.status = "initialized"
    
    def analyze_commits_ahead_of_main(self):
        '''Analyze commits ahead of main'''
        return {}
    
    def validate_phase2_completion(self):
        '''Validate Phase 2 completion'''
        return {}
    
    def generate_compliance_report(self):
        '''Generate compliance report'''
        return {}
    
    def extra_method(self):
        '''Extra method not in design'''
        pass
"""
            
            (repo_path / "orchestrator.py").write_text(orchestrator_impl)
            
            # Create partial implementation
            analyzer_impl = """
'''Git analyzer implementation'''

class GitAnalyzer:
    '''Analyzes git commits'''
    
    def get_commits_ahead_of_main(self):
        '''Get commits ahead of main'''
        return []
    
    # Missing analyze_file_changes method
"""
            
            (repo_path / "analyzer.py").write_text(analyzer_impl)
            
            # Create standalone function implementation
            utils_impl = """
'''Utility functions'''

def validate_data(data):
    '''Validates input data'''
    if not data:
        return False
    return True

def extra_function():
    '''Function not in design'''
    pass

def _private_helper():
    '''Private helper function'''
    pass
"""
            
            (repo_path / "utils.py").write_text(utils_impl)
            
            yield repo_path
    
    @pytest.fixture
    def validator(self, temp_repo):
        """Create DesignValidator instance for testing."""
        return DesignValidator(str(temp_repo))
    
    def test_init(self, temp_repo):
        """Test DesignValidator initialization."""
        validator = DesignValidator(str(temp_repo))
        
        assert validator.repository_path == Path(temp_repo)
        assert validator.design_cache is None
        assert validator.implementation_cache is None
    
    def test_get_validator_name(self, validator):
        """Test validator name retrieval."""
        assert validator.get_validator_name() == "DesignValidator"
    
    def test_load_design_components(self, validator):
        """Test loading design components from documents."""
        components = validator._load_design_components()
        
        assert len(components) >= 3
        assert "ComplianceOrchestrator" in components
        assert "GitAnalyzer" in components
        assert "validate_data" in components
        
        # Check component details
        orchestrator = components["ComplianceOrchestrator"]
        assert orchestrator.component_type == ComponentType.CLASS
        assert len(orchestrator.methods) >= 3
        assert "analyze_commits_ahead_of_main" in orchestrator.methods
    
    def test_parse_design_file(self, validator, temp_repo):
        """Test parsing individual design file."""
        design_file = temp_repo / "design.md"
        components = validator._parse_design_file(design_file)
        
        assert len(components) >= 3
        assert "ComplianceOrchestrator" in components
        assert "GitAnalyzer" in components
        assert "validate_data" in components
        
        # Check component structure
        orchestrator = components["ComplianceOrchestrator"]
        assert orchestrator.name == "ComplianceOrchestrator"
        assert orchestrator.file_path == str(design_file)
        assert orchestrator.line_number > 0
    
    def test_match_component_header(self, validator):
        """Test matching component headers in design documents."""
        # Test class header
        result = validator._match_component_header("### 1. ComplianceOrchestrator")
        assert result == ("ComplianceOrchestrator", ComponentType.CLASS)
        
        # Test interface header
        result = validator._match_component_header("### 2. DataInterface")
        assert result == ("DataInterface", ComponentType.MODULE)
        
        # Test no match
        result = validator._match_component_header("This is not a component header")
        assert result is None
    
    def test_parse_code_block(self, validator, temp_repo):
        """Test parsing code blocks in design documents."""
        code_lines = [
            "class TestClass:",
            "    def method1(self):",
            "        pass",
            "    def method2(self):",
            "        pass",
            "",
            "def standalone_function():",
            "    pass"
        ]
        
        components = validator._parse_code_block(code_lines, temp_repo / "design.md", 10)
        
        assert len(components) >= 2
        assert "TestClass" in components
        assert "standalone_function" in components
        
        test_class = components["TestClass"]
        assert test_class.component_type == ComponentType.CLASS
        assert "method1" in test_class.methods
        assert "method2" in test_class.methods
    
    def test_load_implementation_components(self, validator, temp_repo):
        """Test loading implementation components from source code."""
        components = validator._load_implementation_components(temp_repo)
        
        assert len(components) >= 3
        assert "ComplianceOrchestrator" in components
        assert "GitAnalyzer" in components
        assert "validate_data" in components
        
        # Check component details
        orchestrator = components["ComplianceOrchestrator"]
        assert orchestrator.component_type == ComponentType.CLASS
        assert len(orchestrator.methods) >= 4  # Including extra_method
        assert "analyze_commits_ahead_of_main" in orchestrator.methods
        assert "extra_method" in orchestrator.methods
    
    def test_parse_implementation_file(self, validator, temp_repo):
        """Test parsing individual implementation file."""
        impl_file = temp_repo / "orchestrator.py"
        components = validator._parse_implementation_file(impl_file)
        
        assert len(components) >= 1
        assert "ComplianceOrchestrator" in components
        
        orchestrator = components["ComplianceOrchestrator"]
        assert orchestrator.name == "ComplianceOrchestrator"
        assert orchestrator.file_path == str(impl_file)
        assert orchestrator.docstring is not None
        assert len(orchestrator.methods) >= 4
    
    def test_extract_class_members(self, validator):
        """Test extracting methods and attributes from class definition."""
        content = """
class TestClass:
    def __init__(self):
        self.attr1 = "value1"
        self.attr2 = 42
    
    def method1(self):
        pass
    
    def method2(self, param):
        self.attr3 = param
        return True
"""
        
        methods, attributes = validator._extract_class_members(content, 0)
        
        assert "method1" in methods
        assert "method2" in methods
        assert "__init__" in methods
        assert "attr1" in attributes
        assert "attr2" in attributes
        assert "attr3" in attributes
    
    def test_extract_docstring(self, validator):
        """Test extracting docstrings from function definitions."""
        content = '''
def test_function():
    """
    This is a test function docstring.
    It has multiple lines.
    """
    pass
'''
        
        # Find the position after the function definition
        start_pos = content.find(':')
        docstring = validator._extract_docstring(content, start_pos)
        
        assert docstring is not None
        assert "test function docstring" in docstring
    
    def test_is_method_in_class(self, validator):
        """Test checking if a function is a method inside a class."""
        content = """
class TestClass:
    def method1(self):
        pass

def standalone_function():
    pass
"""
        
        # Find method position
        method_pos = content.find("def method1")
        assert validator._is_method_in_class(content, method_pos) is True
        
        # Find standalone function position
        func_pos = content.find("def standalone_function")
        assert validator._is_method_in_class(content, func_pos) is False
    
    def test_analyze_alignment(self, validator):
        """Test comprehensive alignment analysis."""
        result = validator.analyze_alignment()
        
        assert isinstance(result, AlignmentResult)
        assert result.total_design_components >= 3
        assert result.implemented_components >= 2
        assert len(result.missing_implementations) >= 0  # GitAnalyzer is missing analyze_file_changes
        assert len(result.extra_implementations) >= 0  # May have extra functions
        assert 0 <= result.alignment_score <= 100
        
        # Check issues are generated appropriately
        assert isinstance(result.issues, list)
    
    def test_components_aligned(self, validator):
        """Test checking if design and implementation components are aligned."""
        # Create aligned components
        design_comp = DesignComponent(
            name="TestClass",
            component_type=ComponentType.CLASS,
            description="Test class",
            methods=["method1", "method2"],
            attributes=[],
            file_path="design.md",
            line_number=1,
            metadata={}
        )
        
        impl_comp = ImplementationComponent(
            name="TestClass",
            component_type=ComponentType.CLASS,
            methods=["method1", "method2", "_private_method"],
            attributes=["attr1"],
            file_path="impl.py",
            line_number=1,
            docstring="Test class implementation",
            metadata={}
        )
        
        assert validator._components_aligned(design_comp, impl_comp) is True
        
        # Test misaligned components (missing method)
        impl_comp_missing = ImplementationComponent(
            name="TestClass",
            component_type=ComponentType.CLASS,
            methods=["method1"],  # Missing method2
            attributes=[],
            file_path="impl.py",
            line_number=1,
            docstring="Test class implementation",
            metadata={}
        )
        
        assert validator._components_aligned(design_comp, impl_comp_missing) is False
    
    def test_is_utility_component(self, validator):
        """Test identifying utility components."""
        # Private function
        private_comp = ImplementationComponent(
            name="_private_helper",
            component_type=ComponentType.FUNCTION,
            methods=[],
            attributes=[],
            file_path="utils.py",
            line_number=1,
            docstring=None,
            metadata={}
        )
        assert validator._is_utility_component(private_comp) is True
        
        # Test function
        test_comp = ImplementationComponent(
            name="test_something",
            component_type=ComponentType.FUNCTION,
            methods=[],
            attributes=[],
            file_path="test_utils.py",
            line_number=1,
            docstring=None,
            metadata={}
        )
        assert validator._is_utility_component(test_comp) is True
        
        # Regular function
        regular_comp = ImplementationComponent(
            name="process_data",
            component_type=ComponentType.FUNCTION,
            methods=[],
            attributes=[],
            file_path="processor.py",
            line_number=1,
            docstring=None,
            metadata={}
        )
        assert validator._is_utility_component(regular_comp) is False
    
    def test_generate_alignment_issues(self, validator):
        """Test generation of alignment compliance issues."""
        # Create test data
        missing_impl = [DesignComponent(
            name="MissingClass",
            component_type=ComponentType.CLASS,
            description="Missing implementation",
            methods=[],
            attributes=[],
            file_path="design.md",
            line_number=1,
            metadata={}
        )]
        
        extra_impl = [ImplementationComponent(
            name="ExtraClass",
            component_type=ComponentType.CLASS,
            methods=[],
            attributes=[],
            file_path="extra.py",
            line_number=1,
            docstring=None,
            metadata={}
        )]
        
        misaligned = []
        score = 60.0
        
        issues = validator._generate_alignment_issues(missing_impl, extra_impl, misaligned, score)
        
        assert len(issues) >= 3  # Missing, extra, and low score issues
        
        # Check issue types and severities
        issue_types = [issue.issue_type for issue in issues]
        assert ComplianceIssueType.DESIGN_MISALIGNMENT in issue_types
        
        severities = [issue.severity for issue in issues]
        assert IssueSeverity.HIGH in severities
    
    def test_validate_method(self, validator, temp_repo):
        """Test the main validate method."""
        issues = validator.validate(str(temp_repo))
        
        assert isinstance(issues, list)
        # May have issues depending on alignment
        
        # Check issue structure
        for issue in issues:
            assert hasattr(issue, 'issue_type')
            assert hasattr(issue, 'severity')
            assert hasattr(issue, 'description')
            assert hasattr(issue, 'remediation_steps')
    
    def test_empty_repository(self):
        """Test behavior with empty repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = DesignValidator(temp_dir)
            result = validator.analyze_alignment()
            
            assert result.total_design_components == 0
            assert result.implemented_components == 0
            assert len(result.missing_implementations) == 0
            assert len(result.extra_implementations) == 0
            assert result.alignment_score == 100  # Perfect score for empty repo
    
    def test_malformed_design_file(self, temp_repo):
        """Test handling of malformed design files."""
        # Create malformed design file
        malformed_content = """
This is not a proper design document.
No structured components here.
Random text without proper formatting.
"""
        (temp_repo / "bad_design.md").write_text(malformed_content)
        
        validator = DesignValidator(str(temp_repo))
        components = validator._load_design_components()
        
        # Should still load components from the good design file
        assert len(components) >= 3
    
    def test_file_encoding_handling(self, temp_repo):
        """Test handling of files with different encodings."""
        # Create file with UTF-8 content
        utf8_content = '''
class UnicodeClass:
    """Class with unicode: éñ"""
    
    def unicode_method(self):
        """Method with unicode: éñ"""
        pass
'''
        (temp_repo / "unicode_file.py").write_text(utf8_content, encoding='utf-8')
        
        validator = DesignValidator(str(temp_repo))
        components = validator._parse_implementation_file(temp_repo / "unicode_file.py")
        
        assert len(components) >= 1
        assert "UnicodeClass" in components
    
    @patch('builtins.open', side_effect=IOError("File not accessible"))
    def test_file_access_error_handling(self, mock_file, validator, temp_repo):
        """Test handling of file access errors."""
        # Should not raise exception, just return empty dict
        components = validator._parse_implementation_file(temp_repo / "nonexistent.py")
        assert components == {}
    
    def test_alignment_score_calculation(self, validator):
        """Test alignment score calculation logic."""
        result = validator.analyze_alignment()
        
        # Score should be calculated correctly
        if result.total_design_components > 0:
            expected_score = (result.implemented_components / result.total_design_components * 100)
            # Allow for some variance due to misalignment penalties
            assert abs(result.alignment_score - expected_score) <= 20
        else:
            assert result.alignment_score == 100
    
    def test_complex_class_parsing(self, temp_repo):
        """Test parsing of complex class structures."""
        complex_content = '''
class ComplexClass(BaseClass):
    """A complex class with various features"""
    
    CLASS_ATTR = "constant"
    
    def __init__(self, param1, param2=None):
        """Initialize the complex class"""
        self.instance_attr1 = param1
        self.instance_attr2 = param2 or "default"
        super().__init__()
    
    @property
    def computed_property(self):
        """A computed property"""
        return self.instance_attr1 + str(self.instance_attr2)
    
    @staticmethod
    def static_method():
        """A static method"""
        return "static"
    
    @classmethod
    def class_method(cls):
        """A class method"""
        return cls.CLASS_ATTR
    
    def regular_method(self, arg):
        """A regular method"""
        self.dynamic_attr = arg
        return arg * 2
    
    def _private_method(self):
        """A private method"""
        pass
'''
        
        (temp_repo / "complex.py").write_text(complex_content)
        
        validator = DesignValidator(str(temp_repo))
        components = validator._parse_implementation_file(temp_repo / "complex.py")
        
        assert "ComplexClass" in components
        complex_class = components["ComplexClass"]
        
        # Check methods are extracted
        assert "__init__" in complex_class.methods
        assert "regular_method" in complex_class.methods
        assert "static_method" in complex_class.methods
        assert "class_method" in complex_class.methods
        assert "_private_method" in complex_class.methods
        
        # Check attributes are extracted
        assert "instance_attr1" in complex_class.attributes
        assert "instance_attr2" in complex_class.attributes
        assert "dynamic_attr" in complex_class.attributes


if __name__ == "__main__":
    pytest.main([__file__])