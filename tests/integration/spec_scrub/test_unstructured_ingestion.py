"""
Integration tests for Unstructured Requirements Ingestion

Tests the transformation of messy, real-world requirements into EARS-compliant format.
"""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.spec_scrub.ingestion.unstructured_requirements_ingester import (
    UnstructuredRequirementsIngester,
    RequirementSource,
    UnstructuredRequirement
)


class TestUnstructuredRequirementsIngestion:
    """Test ingestion of unstructured requirements from outside the Fort."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.ingester = UnstructuredRequirementsIngester()
        
    def test_ingester_initialization(self):
        """Test ingester initializes correctly."""
        assert self.ingester is not None
        assert self.ingester.ready() is True
        assert self.ingester.status() == "ready"
        
        health = self.ingester.health()
        assert health["status"] == "healthy"
        assert health["transformation_ready"] is True
        
    def test_ingest_email_requirements(self):
        """Test ingesting requirements from email-style text."""
        email_text = """
        Hi team,
        
        We need the login system to be more secure. Users must be able to authenticate 
        with two-factor authentication. This is critical for our security compliance.
        
        Also, the system should remember user preferences and the dashboard must load 
        within 2 seconds. These are high priority items.
        
        Nice to have: users can customize their profile themes.
        
        Thanks,
        Product Manager
        """
        
        requirements = self.ingester.ingest_from_text(
            email_text, 
            RequirementSource.EMAIL,
            context="Security enhancement request",
            stakeholder="Product Manager"
        )
        
        assert len(requirements) > 0
        
        # Transform to EARS format
        ears_requirements = self.ingester.batch_transform(requirements)
        
        print(f"Email Ingestion Results:")
        print(f"  Raw requirements found: {len(requirements)}")
        print(f"  EARS requirements generated: {len(ears_requirements)}")
        
        for ears_req in ears_requirements:
            print(f"    {ears_req.requirement_id}: {ears_req.user_story}")
            print(f"      Priority: {ears_req.priority}, Category: {ears_req.category}")
            print(f"      Confidence: {ears_req.confidence_score:.2f}")
            for criteria in ears_req.acceptance_criteria:
                print(f"      - {criteria}")
            print()
            
        # Verify EARS compliance
        for ears_req in ears_requirements:
            assert ears_req.requirement_id.startswith("REQ-EMAIL-")
            assert ears_req.user_story
            assert len(ears_req.acceptance_criteria) > 0
            assert 1 <= ears_req.priority <= 5
            assert ears_req.category in ['functional', 'security', 'performance', 'usability']
            
    def test_ingest_jira_ticket(self):
        """Test ingesting requirements from JIRA-style ticket."""
        jira_text = """
        PROJ-123: Implement user dashboard
        
        Priority: High
        Component: Frontend
        
        Description:
        As a logged-in user, I want to see a personalized dashboard so that I can 
        quickly access my most important information.
        
        Acceptance Criteria:
        - When user logs in, then dashboard should display within 3 seconds
        - Given user has notifications, when dashboard loads, then notifications should be visible
        - The dashboard must show recent activity for the last 30 days
        
        Labels: dashboard, frontend, user-experience
        """
        
        requirements = self.ingester.ingest_from_text(
            jira_text,
            RequirementSource.JIRA,
            context="PROJ-123 Dashboard Implementation",
            stakeholder="Development Team"
        )
        
        ears_requirements = self.ingester.batch_transform(requirements)
        
        print(f"JIRA Ingestion Results:")
        for ears_req in ears_requirements:
            print(f"  {ears_req.requirement_id}: {ears_req.user_story}")
            print(f"    Confidence: {ears_req.confidence_score:.2f}")
            
        # JIRA should have higher confidence due to structured format
        assert any(req.confidence_score > 0.7 for req in ears_requirements)
        
    def test_ingest_meeting_notes(self):
        """Test ingesting requirements from meeting notes."""
        meeting_notes = """
        Product Planning Meeting - 2025-01-16
        
        Attendees: PM, Engineering, Design
        
        Key Decisions:
        1. The mobile app must support offline mode for core features
        2. Users should be able to sync data when connection is restored
        3. Performance requirement: app should start in under 2 seconds
        4. Security: all data must be encrypted at rest
        
        Action Items:
        - Engineering to investigate offline storage options
        - Design to create offline mode UI mockups
        - PM to define which features work offline
        
        Next meeting: 2025-01-23
        """
        
        requirements = self.ingester.ingest_from_text(
            meeting_notes,
            RequirementSource.MEETING_NOTES,
            context="Product Planning Meeting",
            stakeholder="Product Team"
        )
        
        ears_requirements = self.ingester.batch_transform(requirements)
        
        print(f"Meeting Notes Ingestion Results:")
        for ears_req in ears_requirements:
            print(f"  {ears_req.requirement_id}: {ears_req.user_story}")
            
        # Should extract multiple requirements from meeting notes
        assert len(ears_requirements) >= 2
        
    def test_ingest_legacy_specification(self):
        """Test ingesting from legacy specification document."""
        legacy_spec = """
        System Requirements Document v1.2
        
        The application shall provide user authentication capabilities.
        Users must be able to register new accounts with email verification.
        Password requirements: minimum 8 characters, must include numbers and symbols.
        
        The system will support role-based access control with the following roles:
        - Administrator: full system access
        - Manager: department-level access  
        - User: personal data access only
        
        Performance Requirements:
        - Login response time: < 500ms
        - Page load time: < 2 seconds
        - System availability: 99.9% uptime
        
        Security Requirements:
        - All communications must use HTTPS
        - Session timeout after 30 minutes of inactivity
        - Failed login attempts locked after 5 tries
        """
        
        requirements = self.ingester.ingest_from_text(
            legacy_spec,
            RequirementSource.LEGACY_SPEC,
            context="Legacy System Requirements v1.2",
            stakeholder="Previous Development Team"
        )
        
        ears_requirements = self.ingester.batch_transform(requirements)
        
        print(f"Legacy Spec Ingestion Results:")
        print(f"  Requirements extracted: {len(ears_requirements)}")
        
        # Group by category
        categories = {}
        for req in ears_requirements:
            categories[req.category] = categories.get(req.category, 0) + 1
            
        print(f"  Categories found: {categories}")
        
        # Should find multiple categories
        assert len(categories) >= 2
        assert 'security' in categories or 'performance' in categories
        
    def test_ingest_from_file(self):
        """Test ingesting requirements from a file."""
        content = """
        Feature Request: Advanced Search
        
        Users need better search capabilities. The current search is too basic.
        
        Requirements:
        - Search should support filters by date, category, and status
        - Results must be returned within 1 second
        - Search should work with partial matches
        - Users should be able to save search queries
        """
        
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            f.flush()
            
            try:
                requirements = self.ingester.ingest_from_file(
                    Path(f.name),
                    RequirementSource.FEATURE_REQUEST
                )
                
                ears_requirements = self.ingester.batch_transform(requirements)
                
                print(f"File Ingestion Results:")
                for req in ears_requirements:
                    print(f"  {req.requirement_id}: {req.user_story}")
                    
                assert len(ears_requirements) > 0
                
            finally:
                Path(f.name).unlink()
                
    def test_confidence_scoring(self):
        """Test confidence scoring for different requirement qualities."""
        test_cases = [
            # High confidence: well-structured with EARS format
            ("WHEN user clicks login THEN system SHALL authenticate credentials", 0.8),
            
            # Medium confidence: clear requirement but not EARS format  
            ("The system must validate user passwords", 0.6),
            
            # Lower confidence: vague requirement
            ("Make the app better", 0.5),
        ]
        
        for text, expected_min_confidence in test_cases:
            req = UnstructuredRequirement(
                source=RequirementSource.JIRA,
                raw_text=text,
                context="Test",
                stakeholder="Test"
            )
            
            ears_req = self.ingester.transform_to_ears(req)
            
            print(f"Confidence Test: '{text}' -> {ears_req.confidence_score:.2f}")
            assert ears_req.confidence_score >= expected_min_confidence - 0.1
            
    def test_priority_extraction(self):
        """Test priority extraction from unstructured text."""
        priority_tests = [
            ("This is a critical security issue", 1),
            ("High priority feature request", 2), 
            ("Normal enhancement for next release", 3),
            ("Nice to have improvement", 4),
        ]
        
        for text, expected_priority in priority_tests:
            # Use the ingestion process to properly extract hints
            requirements = self.ingester.ingest_from_text(text, RequirementSource.EMAIL, "Test", "Test")
            assert len(requirements) > 0
            
            req = requirements[0]
            ears_req = self.ingester.transform_to_ears(req)
            
            print(f"Priority Test: '{text}' -> Hint: {req.priority_hint} -> Priority {ears_req.priority}")
            assert ears_req.priority == expected_priority
            
    def test_category_detection(self):
        """Test category detection from requirement content."""
        category_tests = [
            ("User authentication and security features", "security"),
            ("System performance and response times", "performance"),
            ("User interface and experience improvements", "usability"),
            ("Data processing and business logic", "functional"),
        ]
        
        for text, expected_category in category_tests:
            # Use the ingestion process to properly extract hints
            requirements = self.ingester.ingest_from_text(text, RequirementSource.FEATURE_REQUEST, "Test", "Test")
            assert len(requirements) > 0
            
            req = requirements[0]
            ears_req = self.ingester.transform_to_ears(req)
            
            print(f"Category Test: '{text}' -> Hint: {req.category_hint} -> {ears_req.category}")
            assert ears_req.category == expected_category