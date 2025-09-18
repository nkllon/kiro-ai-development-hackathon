"""
Unit tests for RequirementsParser

Tests the parsing of requirements documents for RDI traceability validation.
"""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from src.spec_scrub.parsers.requirements_parser import (
    RequirementsParser, 
    Requirement, 
    RequirementMetadata
)


class TestRequirementsParser:
    """Test suite for RequirementsParser functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = RequirementsParser()
        
    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        assert self.parser is not None
        assert self.parser.ready() is True
        assert self.parser.status() == "ready"
        
    def test_health_check(self):
        """Test health check returns expected status."""
        health = self.parser.health()
        assert health["status"] == "healthy"
        assert health["patterns_loaded"] == 4
        assert health["component"] == "RequirementsParser"
        
    def test_metrics(self):
        """Test metrics returns expected values."""
        metrics = self.parser.metrics()
        assert "parse_success_rate" in metrics
        assert "average_requirements_per_doc" in metrics
        assert "parsing_time_ms" in metrics
        
    def test_parse_requirements_basic(self):
        """Test parsing basic requirements document."""
        content = """
# Requirements Document

## Introduction
Test requirements document.

## Requirements

### Requirement 1: Basic Functionality

**User Story:** As a user, I want basic functionality, so that I can use the system.

#### Acceptance Criteria

1. WHEN I use the system THEN it SHALL provide basic functionality
2. WHEN I request help THEN the system SHALL provide assistance

### Requirement 2: Advanced Features

**User Story:** As a power user, I want advanced features, so that I can be more productive.

#### Acceptance Criteria

1. WHEN I access advanced mode THEN the system SHALL provide enhanced capabilities
2. IF I have permissions THEN the system SHALL allow advanced operations
"""
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            try:
                requirements = self.parser.parse_requirements(Path(f.name))
                
                assert len(requirements) == 2
                
                # Test first requirement
                req1 = requirements[0]
                assert req1.requirement_id == "1"
                assert "basic functionality" in req1.user_story.lower()
                assert len(req1.acceptance_criteria) == 2
                assert "basic functionality" in req1.acceptance_criteria[0]
                assert req1.source_file == Path(f.name)
                assert req1.line_number > 0
                
                # Test second requirement
                req2 = requirements[1]
                assert req2.requirement_id == "2"
                assert "advanced features" in req2.user_story.lower()
                assert len(req2.acceptance_criteria) == 2
                assert "advanced mode" in req2.acceptance_criteria[0]
                
            finally:
                Path(f.name).unlink()
                
    def test_parse_requirements_with_metadata(self):
        """Test parsing requirements with metadata."""
        content = """
### Requirement 1.1: System Authentication

**User Story:** As a user, I want secure authentication, so that my data is protected.

Priority: 1
Category: security
Dependencies: user-management, encryption
Tags: security, authentication, critical
Complexity: high

#### Acceptance Criteria

1. WHEN I log in THEN the system SHALL verify my credentials
2. WHEN authentication fails THEN the system SHALL log the attempt
"""
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            try:
                requirements = self.parser.parse_requirements(Path(f.name))
                
                assert len(requirements) == 1
                req = requirements[0]
                
                # Test basic parsing
                assert req.requirement_id == "1.1"
                assert "secure authentication" in req.user_story.lower()
                
                # Test metadata extraction
                metadata = self.parser.extract_requirement_metadata(req)
                assert metadata.requirement_id == "1.1"
                assert metadata.priority == 1
                assert metadata.category == "security"
                assert "user-management" in metadata.dependencies
                assert "encryption" in metadata.dependencies
                assert "security" in metadata.tags
                assert "authentication" in metadata.tags
                assert metadata.complexity == "high"
                
            finally:
                Path(f.name).unlink()
                
    def test_parse_requirements_no_user_story(self):
        """Test parsing requirements without explicit user story."""
        content = """
### Requirement 1: Performance Requirements

#### Acceptance Criteria

1. WHEN processing requests THEN the system SHALL respond within 100ms
2. WHEN under load THEN the system SHALL maintain 99.9% uptime
"""
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            try:
                requirements = self.parser.parse_requirements(Path(f.name))
                
                assert len(requirements) == 1
                req = requirements[0]
                
                # Should use requirement title as user story
                assert req.requirement_id == "1"
                assert req.user_story == "Performance Requirements"
                assert len(req.acceptance_criteria) == 2
                
            finally:
                Path(f.name).unlink()
                
    def test_parse_requirements_file_not_found(self):
        """Test parsing non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_requirements(Path("/nonexistent/file.md"))
            
    def test_parse_requirements_invalid_format(self):
        """Test parsing invalid format raises ValueError."""
        content = "This is not a valid requirements document"
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            try:
                requirements = self.parser.parse_requirements(Path(f.name))
                # Should return empty list for invalid format, not raise error
                assert requirements == []
                
            finally:
                Path(f.name).unlink()
                
    def test_extract_acceptance_criteria_various_formats(self):
        """Test extraction of acceptance criteria in various formats."""
        content = """
### Requirement 1: Test Requirement

#### Acceptance Criteria

1. WHEN condition A THEN system SHALL do X
2. IF condition B THEN system SHALL do Y  
3. GIVEN condition C WHEN event D THEN system SHALL do Z
4. The system SHALL always maintain data integrity
"""
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            try:
                requirements = self.parser.parse_requirements(Path(f.name))
                
                assert len(requirements) == 1
                req = requirements[0]
                
                assert len(req.acceptance_criteria) == 4
                assert "WHEN condition A" in req.acceptance_criteria[0]
                assert "IF condition B" in req.acceptance_criteria[1]
                assert "GIVEN condition C" in req.acceptance_criteria[2]
                assert "data integrity" in req.acceptance_criteria[3]
                
            finally:
                Path(f.name).unlink()
                
    def test_extract_metadata_defaults(self):
        """Test metadata extraction with default values."""
        content = """
### Requirement 1: Simple Requirement

**User Story:** As a user, I want something simple.

#### Acceptance Criteria

1. WHEN I do something THEN it SHALL work
"""
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            try:
                requirements = self.parser.parse_requirements(Path(f.name))
                req = requirements[0]
                
                metadata = self.parser.extract_requirement_metadata(req)
                
                # Test default values
                assert metadata.priority == 3  # Default medium priority
                assert metadata.category == "functional"  # Default category
                assert metadata.dependencies == []
                assert metadata.tags == []
                assert metadata.complexity == "medium"
                
            finally:
                Path(f.name).unlink()
                
    def test_parse_hierarchical_requirements(self):
        """Test parsing hierarchical requirement IDs."""
        content = """
### Requirement 1: Parent Requirement

#### Acceptance Criteria
1. Parent requirement criteria

### Requirement 1.1: Child Requirement

#### Acceptance Criteria  
1. Child requirement criteria

### Requirement 1.2.1: Grandchild Requirement

#### Acceptance Criteria
1. Grandchild requirement criteria
"""
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            
            try:
                requirements = self.parser.parse_requirements(Path(f.name))
                
                assert len(requirements) == 3
                assert requirements[0].requirement_id == "1"
                assert requirements[1].requirement_id == "1.1"
                assert requirements[2].requirement_id == "1.2.1"
                
            finally:
                Path(f.name).unlink()


class TestRequirementDataClasses:
    """Test the requirement data classes."""
    
    def test_requirement_creation(self):
        """Test Requirement dataclass creation."""
        req = Requirement(
            requirement_id="1.1",
            user_story="Test user story",
            acceptance_criteria=["Criteria 1", "Criteria 2"],
            priority=1,
            category="functional",
            source_file=Path("test.md"),
            line_number=10
        )
        
        assert req.requirement_id == "1.1"
        assert req.user_story == "Test user story"
        assert len(req.acceptance_criteria) == 2
        assert req.priority == 1
        assert req.category == "functional"
        assert req.source_file == Path("test.md")
        assert req.line_number == 10
        
    def test_requirement_metadata_creation(self):
        """Test RequirementMetadata dataclass creation."""
        metadata = RequirementMetadata(
            requirement_id="1.1",
            dependencies=["req-1", "req-2"],
            priority=2,
            category="security",
            tags=["critical", "auth"],
            complexity="high"
        )
        
        assert metadata.requirement_id == "1.1"
        assert metadata.dependencies == ["req-1", "req-2"]
        assert metadata.priority == 2
        assert metadata.category == "security"
        assert metadata.tags == ["critical", "auth"]
        assert metadata.complexity == "high"