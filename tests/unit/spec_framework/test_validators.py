"""
Unit tests for Spec Framework document validators.

Tests cover validation logic, error reporting, remediation guidance generation,
and caching functionality.
"""

import os
import tempfile
import unittest
import shutil
from datetime import datetime
from pathlib import Path

from src.spec_framework.validators import DocumentValidator, ValidationCache
from src.spec_framework.models import (
    SpecificationDocument,
    SemanticVersion,
    WorkflowStage,
    ApprovalStatus,
    ValidationResult,
    ValidationError,
    ValidationWarning,
)


class TestDocumentValidator(unittest.TestCase):
    """Test document validator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = DocumentValidator()
        
        # Create test specification
        self.test_spec = SpecificationDocument(
            id="test-spec",
            name="Test Specification",
            version=SemanticVersion(1, 0, 0),
            requirements_path=os.path.join(self.temp_dir, "requirements.md")
        )
        
        # Create valid requirements file
        self.create_valid_requirements_file()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def create_valid_requirements_file(self):
        """Create a valid requirements file for testing."""
        content = """# Test Specification Requirements

## Introduction

This is a test specification for validation testing.

## Requirements

### Requirement 1: User Authentication

**User Story:** As a user, I want to authenticate, so that I can access the system

#### Acceptance Criteria

1. WHEN user enters valid credentials THEN system SHALL authenticate user
2. WHEN user enters invalid credentials THEN system SHALL display error message
3. IF user is already authenticated THEN system SHALL redirect to dashboard

### Requirement 2: Data Validation

**User Story:** As a system, I want to validate data, so that data integrity is maintained

#### Acceptance Criteria

1. WHEN data is submitted THEN system SHALL validate format
2. WHILE validation is running THEN system SHALL show loading indicator
"""
        
        with open(self.test_spec.requirements_path, 'w') as f:
            f.write(content)
    
    def create_invalid_requirements_file(self):
        """Create an invalid requirements file for testing."""
        content = """# Test Specification

Some content without proper structure.

No EARS format here.
"""
        
        with open(self.test_spec.requirements_path, 'w') as f:
            f.write(content)
    
    def create_design_file(self):
        """Create a design file for testing."""
        design_path = os.path.join(self.temp_dir, "design.md")
        content = """# Test Specification Design

## Overview

This is the design overview.

## Architecture

System architecture details.

## Components

Component descriptions.
"""
        
        with open(design_path, 'w') as f:
            f.write(content)
        
        self.test_spec.design_path = design_path
        return design_path
    
    def create_tasks_file(self):
        """Create a tasks file for testing."""
        tasks_path = os.path.join(self.temp_dir, "tasks.md")
        content = """# Test Specification Implementation Plan

## Implementation Plan

- [ ] 1. Task one
  - Implement feature A
  - Write tests for feature A
  
- [ ] 2. Task two
  - Implement feature B
  - Write tests for feature B
"""
        
        with open(tasks_path, 'w') as f:
            f.write(content)
        
        self.test_spec.tasks_path = tasks_path
        return tasks_path
    
    def test_validate_structure_valid_requirements(self):
        """Test structure validation with valid requirements file."""
        result = self.validator.validate_structure(self.test_spec)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertIsNotNone(result.validation_timestamp)
    
    def test_validate_structure_missing_file(self):
        """Test structure validation with missing requirements file."""
        # Remove requirements file
        os.remove(self.test_spec.requirements_path)
        
        result = self.validator.validate_structure(self.test_spec)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertEqual(result.errors[0].error_type, "missing_file")
    
    def test_validate_structure_design_stage(self):
        """Test structure validation for design stage."""
        self.test_spec.workflow_stage = WorkflowStage.DESIGN
        
        # Without design file - should fail
        result = self.validator.validate_structure(self.test_spec)
        self.assertFalse(result.is_valid)
        
        # With design file - should pass
        design_path = self.create_design_file()  # This sets self.test_spec.design_path
        
        # Clear cache to ensure fresh validation
        self.validator._validation_cache.clear()
        
        result = self.validator.validate_structure(self.test_spec)
        
        # Debug output
        if not result.is_valid:
            print(f"Design path: {self.test_spec.design_path}")
            print(f"Design file exists: {os.path.exists(self.test_spec.design_path) if self.test_spec.design_path else False}")
            print(f"Errors: {[error.message for error in result.errors]}")
            print(f"Warnings: {[warning.message for warning in result.warnings]}")
        
        self.assertTrue(result.is_valid)
    
    def test_validate_structure_tasks_stage(self):
        """Test structure validation for tasks stage."""
        self.test_spec.workflow_stage = WorkflowStage.TASKS
        design_path = self.create_design_file()  # This sets self.test_spec.design_path
        
        # Without tasks file - should fail
        result = self.validator.validate_structure(self.test_spec)
        self.assertFalse(result.is_valid)
        
        # With tasks file - should pass
        tasks_path = self.create_tasks_file()  # This sets self.test_spec.tasks_path
        
        # Clear cache to ensure fresh validation
        self.validator._validation_cache.clear()
        
        result = self.validator.validate_structure(self.test_spec)
        self.assertTrue(result.is_valid)
    
    def test_validate_ears_format_valid(self):
        """Test EARS format validation with valid format."""
        result = self.validator.validate_ears_format(self.test_spec.requirements_path)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_validate_ears_format_invalid(self):
        """Test EARS format validation with invalid format."""
        self.create_invalid_requirements_file()
        
        result = self.validator.validate_ears_format(self.test_spec.requirements_path)
        
        # Should have warnings about missing acceptance criteria
        self.assertGreater(len(result.warnings), 0)
    
    def test_validate_ears_format_missing_file(self):
        """Test EARS format validation with missing file."""
        os.remove(self.test_spec.requirements_path)
        
        result = self.validator.validate_ears_format(self.test_spec.requirements_path)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].error_type, "missing_file")
    
    def test_validate_completeness_requirements_stage(self):
        """Test completeness validation for requirements stage."""
        result = self.validator.validate_completeness(self.test_spec)
        
        # Should pass with valid requirements file
        self.assertTrue(result.is_valid)
    
    def test_validate_completeness_missing_sections(self):
        """Test completeness validation with missing sections."""
        # Create requirements file without required sections
        content = "# Test\n\nSome content but no proper sections."
        with open(self.test_spec.requirements_path, 'w') as f:
            f.write(content)
        
        result = self.validator.validate_completeness(self.test_spec)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        
        # Check that missing sections are identified
        error_messages = [error.message for error in result.errors]
        self.assertTrue(any("Introduction" in msg for msg in error_messages))
        self.assertTrue(any("Requirements" in msg for msg in error_messages))
    
    def test_validate_workflow_compliance_valid(self):
        """Test workflow compliance validation with valid progression."""
        result = self.validator.validate_workflow_compliance(self.test_spec)
        
        # Requirements stage should be valid
        self.assertTrue(result.is_valid)
    
    def test_validate_workflow_compliance_violations(self):
        """Test workflow compliance validation with violations."""
        # Set to design stage without design file
        self.test_spec.workflow_stage = WorkflowStage.DESIGN
        self.test_spec.design_path = None
        
        result = self.validator.validate_workflow_compliance(self.test_spec)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertEqual(result.errors[0].error_type, "workflow_violation")
    
    def test_validate_workflow_compliance_approval_warnings(self):
        """Test workflow compliance validation with approval inconsistencies."""
        # Set approved status on requirements stage
        self.test_spec.approval_status = ApprovalStatus.APPROVED
        
        result = self.validator.validate_workflow_compliance(self.test_spec)
        
        # Should have warnings about unusual approval status
        self.assertGreater(len(result.warnings), 0)
        self.assertEqual(result.warnings[0].warning_type, "approval_inconsistency")
    
    def test_generate_validation_report(self):
        """Test comprehensive validation report generation."""
        report = self.validator.generate_validation_report(self.test_spec)
        
        self.assertIn("Validation Report", report)
        self.assertIn(self.test_spec.name, report)
        self.assertIn(self.test_spec.id, report)
        self.assertIn("Structure Validation", report)
        self.assertIn("EARS Format Validation", report)
        self.assertIn("Completeness Validation", report)
        self.assertIn("Workflow Validation", report)
        self.assertIn("Overall Status", report)
    
    def test_generate_remediation_guidance_valid(self):
        """Test remediation guidance for valid document."""
        result = ValidationResult(is_valid=True)
        
        guidance = self.validator.generate_remediation_guidance(result)
        
        self.assertEqual(guidance.error_type, "none")
        self.assertIn("No issues found", guidance.specific_guidance)
    
    def test_generate_remediation_guidance_missing_file(self):
        """Test remediation guidance for missing file errors."""
        error = ValidationError(
            error_type="missing_file",
            message="Requirements file not found",
            location="requirements.md"
        )
        result = ValidationResult(is_valid=False, errors=[error])
        
        guidance = self.validator.generate_remediation_guidance(result)
        
        self.assertEqual(guidance.error_type, "missing_file")
        self.assertIn("Create the missing files", guidance.specific_guidance)
        self.assertGreater(len(guidance.examples), 0)
        self.assertGreater(len(guidance.templates), 0)
    
    def test_generate_remediation_guidance_ears_format(self):
        """Test remediation guidance for EARS format errors."""
        error = ValidationError(
            error_type="ears_format_error",
            message="Criterion does not follow EARS format",
            location="acceptance_criteria_1.1"
        )
        result = ValidationResult(is_valid=False, errors=[error])
        
        guidance = self.validator.generate_remediation_guidance(result)
        
        self.assertEqual(guidance.error_type, "ears_format_error")
        self.assertIn("EARS", guidance.specific_guidance)
        self.assertGreater(len(guidance.examples), 0)
        
        # Check that examples contain EARS patterns
        examples_text = " ".join(guidance.examples)
        self.assertTrue(any(pattern in examples_text for pattern in ["WHEN", "THEN", "SHALL"]))
    
    def test_validation_caching(self):
        """Test validation result caching functionality."""
        # First validation should compute result
        result1 = self.validator.validate_structure(self.test_spec)
        
        # Second validation should use cached result
        result2 = self.validator.validate_structure(self.test_spec)
        
        # Results should be identical (same timestamp indicates caching)
        self.assertEqual(result1.validation_timestamp, result2.validation_timestamp)
    
    def test_validation_cache_expiry(self):
        """Test validation cache expiry functionality."""
        # Create validator with very short cache TTL
        validator = DocumentValidator(cache_ttl_seconds=0)
        
        # First validation
        result1 = validator.validate_structure(self.test_spec)
        
        # Second validation should recompute (cache expired)
        result2 = validator.validate_structure(self.test_spec)
        
        # Results should have different timestamps
        self.assertNotEqual(result1.validation_timestamp, result2.validation_timestamp)
    
    def test_ears_pattern_matching(self):
        """Test EARS pattern matching functionality."""
        # Test valid EARS patterns
        valid_patterns = [
            "WHEN user clicks button THEN system SHALL respond",
            "IF condition is true THEN system SHALL execute action",
            "WHILE process is running THEN system SHALL show progress"
        ]
        
        for pattern in valid_patterns:
            matches = any(regex.search(pattern) for regex in self.validator.ears_patterns.values())
            self.assertTrue(matches, f"Pattern should match: {pattern}")
        
        # Test invalid patterns
        invalid_patterns = [
            "User clicks button and system responds",
            "The system should do something when condition occurs",
            "System will respond to user input"
        ]
        
        for pattern in invalid_patterns:
            matches = any(regex.search(pattern) for regex in self.validator.ears_patterns.values())
            self.assertFalse(matches, f"Pattern should not match: {pattern}")
    
    def test_section_extraction(self):
        """Test markdown section extraction functionality."""
        # Create file with various header levels
        test_file = os.path.join(self.temp_dir, "test_sections.md")
        content = """# Main Title

## Section 1

### Subsection 1.1

## Section 2

#### Deep Subsection

## Section 3
"""
        
        with open(test_file, 'w') as f:
            f.write(content)
        
        sections = self.validator._extract_sections(test_file)
        
        expected_sections = {"Main Title", "Section 1", "Subsection 1.1", "Section 2", "Deep Subsection", "Section 3"}
        self.assertEqual(sections, expected_sections)


class TestValidationCache(unittest.TestCase):
    """Test validation cache functionality."""
    
    def test_cache_expiry_check(self):
        """Test cache expiry checking."""
        from src.spec_framework.models import ValidationResult
        
        # Create cache entry
        result = ValidationResult(is_valid=True)
        cache = ValidationCache(
            spec_id="test",
            result=result,
            timestamp=datetime.now(),
            file_hash="hash123"
        )
        
        # Should not be expired immediately
        self.assertFalse(cache.is_expired(ttl_seconds=300))
        
        # Should be expired with 0 TTL
        self.assertTrue(cache.is_expired(ttl_seconds=0))


if __name__ == "__main__":
    unittest.main()