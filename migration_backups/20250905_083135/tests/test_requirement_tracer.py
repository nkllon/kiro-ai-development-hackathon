"""
Unit tests for RequirementTracer class.

Tests requirement traceability detection and validation functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from src.beast_mode.compliance.rdi.requirement_tracer import (
    RequirementTracer,
    RequirementDefinition,
    RequirementReference,
    TraceabilityResult
)
from src.beast_mode.compliance.models import ComplianceIssueType, IssueSeverity


class TestRequirementTracer:
    """Test cases for RequirementTracer class."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Create requirements document
            requirements_content = """
# Requirements Document

## Requirements

### Requirement 1.1

**User Story:** As a developer, I want to validate code, so that I can ensure quality.

#### Acceptance Criteria

1. WHEN code is analyzed THEN the system SHALL validate syntax
2. WHEN validation fails THEN the system SHALL report errors

### Requirement 2.1

**User Story:** As a user, I want to generate reports, so that I can track progress.

#### Acceptance Criteria

1. WHEN reports are requested THEN the system SHALL generate comprehensive reports
"""
            
            (repo_path / "requirements.md").write_text(requirements_content)
            
            # Create implementation file with requirement references
            impl_content = """
def validate_code():
    '''
    Validates code syntax and structure.
    _Requirements: 1.1_
    '''
    pass

def process_data():
    '''
    Processes data without requirement reference.
    '''
    pass

# This function implements requirement 2.1
def generate_report():
    '''Generate comprehensive report'''
    # Requirements: 2.1
    pass
"""
            
            (repo_path / "implementation.py").write_text(impl_content)
            
            # Create test file
            test_content = """
def test_validate_code():
    '''Test code validation - Requirements: 1.1'''
    pass

def test_orphaned_requirement():
    '''Test for non-existent requirement - Requirements: 3.1'''
    pass
"""
            
            (repo_path / "test_implementation.py").write_text(test_content)
            
            yield repo_path
    
    @pytest.fixture
    def tracer(self, temp_repo):
        """Create RequirementTracer instance for testing."""
        return RequirementTracer(str(temp_repo))
    
    def test_init(self, temp_repo):
        """Test RequirementTracer initialization."""
        tracer = RequirementTracer(str(temp_repo))
        
        assert tracer.repository_path == Path(temp_repo)
        assert tracer.requirements_cache is None
        assert len(tracer.requirement_patterns) > 0
    
    def test_get_validator_name(self, tracer):
        """Test validator name retrieval."""
        assert tracer.get_validator_name() == "RequirementTracer"
    
    def test_load_requirements(self, tracer):
        """Test loading requirements from documents."""
        requirements = tracer._load_requirements()
        
        assert len(requirements) == 2
        assert "1.1" in requirements
        assert "2.1" in requirements
        
        req_1_1 = requirements["1.1"]
        assert req_1_1.requirement_id == "1.1"
        assert "developer" in req_1_1.description.lower()
        assert len(req_1_1.acceptance_criteria) == 2
    
    def test_parse_requirements_file(self, tracer, temp_repo):
        """Test parsing individual requirements file."""
        req_file = temp_repo / "requirements.md"
        requirements = tracer._parse_requirements_file(req_file)
        
        assert len(requirements) == 2
        assert "1.1" in requirements
        assert "2.1" in requirements
        
        # Check requirement details
        req_1_1 = requirements["1.1"]
        assert req_1_1.requirement_id == "1.1"
        assert req_1_1.file_path == str(req_file)
        assert req_1_1.line_number > 0
        assert len(req_1_1.acceptance_criteria) == 2
    
    def test_find_requirement_references(self, tracer, temp_repo):
        """Test finding requirement references in files."""
        references = tracer._find_requirement_references(temp_repo)
        
        # Should find references in both implementation and test files
        assert len(references) >= 3
        
        # Check for specific references
        ref_ids = [ref.requirement_id for ref in references]
        assert "1.1" in ref_ids
        assert "2.1" in ref_ids
        assert "3.1" in ref_ids  # Orphaned reference
        
        # Check reference types
        ref_types = [ref.reference_type for ref in references]
        assert "implementation" in ref_types
        assert "test" in ref_types
    
    def test_find_references_in_file(self, tracer, temp_repo):
        """Test finding references in a single file."""
        impl_file = temp_repo / "implementation.py"
        references = tracer._find_references_in_file(impl_file)
        
        assert len(references) >= 2
        
        # Check that references are found
        ref_ids = [ref.requirement_id for ref in references]
        assert "1.1" in ref_ids
        assert "2.1" in ref_ids
        
        # Check file paths are correct
        for ref in references:
            assert ref.file_path == str(impl_file)
            assert ref.line_number > 0
    
    def test_determine_reference_type(self, tracer, temp_repo):
        """Test determining reference type from context."""
        # Test file reference
        test_file = temp_repo / "test_implementation.py"
        ref_type = tracer._determine_reference_type("# Requirements: 1.1", test_file)
        assert ref_type == "test"
        
        # Comment reference
        ref_type = tracer._determine_reference_type("# Requirements: 1.1", temp_repo / "code.py")
        assert ref_type == "comment"
        
        # Docstring reference
        ref_type = tracer._determine_reference_type('"""Requirements: 1.1"""', temp_repo / "code.py")
        assert ref_type == "docstring"
        
        # Implementation reference
        ref_type = tracer._determine_reference_type("_Requirements: 1.1_", temp_repo / "code.py")
        assert ref_type == "implementation"
    
    def test_analyze_traceability(self, tracer):
        """Test comprehensive traceability analysis."""
        result = tracer.analyze_traceability()
        
        assert isinstance(result, TraceabilityResult)
        assert result.total_requirements == 2
        assert result.traced_requirements >= 2  # Both requirements should be traced
        assert len(result.untraced_requirements) == 0  # All requirements are traced
        assert len(result.orphaned_implementations) >= 1  # Should find orphaned reference to 3.1
        assert 0 <= result.traceability_score <= 100
        
        # Check issues are generated appropriately
        assert isinstance(result.issues, list)
    
    def test_generate_traceability_issues(self, tracer):
        """Test generation of traceability compliance issues."""
        # Test with untraced requirements
        untraced = ["1.1", "2.1"]
        orphaned = []
        score = 50.0
        
        issues = tracer._generate_traceability_issues(untraced, orphaned, score)
        
        assert len(issues) >= 2  # Should have issues for untraced requirements and low score
        
        # Check issue types and severities
        issue_types = [issue.issue_type for issue in issues]
        assert ComplianceIssueType.REQUIREMENT_TRACEABILITY in issue_types
        
        severities = [issue.severity for issue in issues]
        assert IssueSeverity.HIGH in severities
    
    def test_validate_method(self, tracer, temp_repo):
        """Test the main validate method."""
        issues = tracer.validate(str(temp_repo))
        
        assert isinstance(issues, list)
        # Should have at least one issue for orphaned implementation
        assert len(issues) >= 1
        
        # Check issue structure
        for issue in issues:
            assert hasattr(issue, 'issue_type')
            assert hasattr(issue, 'severity')
            assert hasattr(issue, 'description')
            assert hasattr(issue, 'remediation_steps')
    
    def test_empty_repository(self):
        """Test behavior with empty repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracer = RequirementTracer(temp_dir)
            result = tracer.analyze_traceability()
            
            assert result.total_requirements == 0
            assert result.traced_requirements == 0
            assert len(result.untraced_requirements) == 0
            assert len(result.orphaned_implementations) == 0
            assert result.traceability_score == 0
    
    def test_malformed_requirements_file(self, temp_repo):
        """Test handling of malformed requirements files."""
        # Create malformed requirements file
        malformed_content = """
This is not a proper requirements document.
No structured requirements here.
"""
        (temp_repo / "bad_requirements.md").write_text(malformed_content)
        
        tracer = RequirementTracer(str(temp_repo))
        requirements = tracer._load_requirements()
        
        # Should still load the good requirements file
        assert len(requirements) >= 2
    
    def test_multiple_requirement_patterns(self, temp_repo):
        """Test recognition of different requirement reference patterns."""
        # Create file with various reference patterns
        patterns_content = """
# Different requirement reference patterns
def func1():
    # _Requirements: 1.1, 2.1_
    pass

def func2():
    # Requirement 1.1
    pass

def func3():
    # REQ-2.1
    pass

def func4():
    # # 1.1
    pass
"""
        
        (temp_repo / "patterns.py").write_text(patterns_content)
        
        tracer = RequirementTracer(str(temp_repo))
        references = tracer._find_references_in_file(temp_repo / "patterns.py")
        
        # Should find multiple references with different patterns
        assert len(references) >= 4
        
        ref_ids = [ref.requirement_id for ref in references]
        assert "1.1" in ref_ids
        assert "2.1" in ref_ids
    
    def test_file_encoding_handling(self, temp_repo):
        """Test handling of files with different encodings."""
        # Create file with UTF-8 content
        utf8_content = "# Requirements: 1.1 - Testing with special chars: éñ"
        (temp_repo / "utf8_file.py").write_text(utf8_content, encoding='utf-8')
        
        tracer = RequirementTracer(str(temp_repo))
        references = tracer._find_references_in_file(temp_repo / "utf8_file.py")
        
        assert len(references) >= 1
        assert references[0].requirement_id == "1.1"
    
    @patch('builtins.open', side_effect=IOError("File not accessible"))
    def test_file_access_error_handling(self, mock_file, tracer, temp_repo):
        """Test handling of file access errors."""
        # Should not raise exception, just return empty list
        references = tracer._find_references_in_file(temp_repo / "nonexistent.py")
        assert references == []
    
    def test_traceability_score_calculation(self, tracer):
        """Test traceability score calculation logic."""
        # Load requirements first
        tracer.requirements_cache = tracer._load_requirements()
        
        result = tracer.analyze_traceability()
        
        # Score should be calculated correctly
        expected_score = (result.traced_requirements / result.total_requirements * 100) if result.total_requirements > 0 else 0
        assert abs(result.traceability_score - expected_score) < 0.1
    
    def test_comma_separated_requirements(self, temp_repo):
        """Test handling of comma-separated requirement lists."""
        # Create file with comma-separated requirements
        multi_req_content = """
def complex_function():
    '''
    This function implements multiple requirements.
    _Requirements: 1.1, 2.1_
    '''
    pass
"""
        
        (temp_repo / "multi_req.py").write_text(multi_req_content)
        
        tracer = RequirementTracer(str(temp_repo))
        references = tracer._find_references_in_file(temp_repo / "multi_req.py")
        
        # Should find separate references for each requirement
        ref_ids = [ref.requirement_id for ref in references]
        assert "1.1" in ref_ids
        assert "2.1" in ref_ids
        assert len([r for r in references if r.requirement_id in ["1.1", "2.1"]]) == 2


if __name__ == "__main__":
    pytest.main([__file__])