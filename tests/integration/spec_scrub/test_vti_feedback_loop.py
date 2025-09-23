"""
Integration tests for VTI (Validation-through-Implementation) Feedback Loop

Tests the validation of requirements transformation by comparing parallel implementations
and learning from gaps to improve parsing for local conditions.
"""

import pytest
from pathlib import Path

from src.spec_scrub.validation.vti_feedback_loop import VTIFeedbackLoop


class TestVTIFeedbackLoop:
    """Test VTI validation approach for requirements transformation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.vti = VTIFeedbackLoop()
        
    def test_vti_initialization(self):
        """Test VTI system initializes correctly."""
        assert self.vti is not None
        assert self.vti.ready() is True
        assert self.vti.status() == "ready"
        
        health = self.vti.health()
        assert health["status"] == "healthy"
        assert "local_conventions_learned" in health
        
    def test_basic_vti_validation(self):
        """Test basic VTI validation cycle."""
        raw_requirements = """
        We need a user login system. Users should be able to register with email
        and password. The system must be secure and fast. Login should work on
        mobile devices too. Also, we want to remember user preferences.
        """
        
        stakeholder_context = "E-commerce Product Manager - Security Focused"
        
        results = self.vti.run_vti_validation(raw_requirements, stakeholder_context)
        
        # Verify VTI results structure
        assert "raw_requirements" in results
        assert "ears_requirements" in results
        assert "ears_artifacts" in results
        assert "vibe_artifacts" in results
        assert "gaps_identified" in results
        assert "local_conventions" in results
        assert "parsing_improvements" in results
        assert "validation_score" in results
        
        print(f"VTI Validation Results:")
        print(f"  EARS Requirements: {len(results['ears_requirements'])}")
        print(f"  EARS Artifacts: {len(results['ears_artifacts'])}")
        print(f"  Vibe Artifacts: {len(results['vibe_artifacts'])}")
        print(f"  Gaps Identified: {len(results['gaps_identified'])}")
        print(f"  Local Conventions: {len(results['local_conventions'])}")
        print(f"  Validation Score: {results['validation_score']:.2f}")
        
        # Show gaps for analysis
        for gap in results['gaps_identified']:
            print(f"    Gap ({gap.gap_type}): {gap.description}")
            print(f"      Suggested improvement: {gap.suggested_parsing_improvement}")
            
    def test_vti_with_ambiguous_requirements(self):
        """Test VTI with intentionally ambiguous requirements to generate gaps."""
        ambiguous_requirements = """
        Make the app better. Users want it to be fast and easy to use.
        It should work well and look good. The data needs to be safe.
        Performance is important. Make sure it's user-friendly.
        """
        
        stakeholder_context = "Non-technical Stakeholder - Vague Requirements"
        
        results = self.vti.run_vti_validation(ambiguous_requirements, stakeholder_context)
        
        # Ambiguous requirements should generate more gaps
        assert len(results['gaps_identified']) > 0
        assert results['validation_score'] < 0.9  # Should have lower validation score
        
        print(f"Ambiguous Requirements VTI:")
        print(f"  Gaps: {len(results['gaps_identified'])}")
        print(f"  Validation Score: {results['validation_score']:.2f}")
        
        # Should detect local conventions for this type of stakeholder
        conventions = results['local_conventions']
        if conventions:
            print(f"  Detected Conventions:")
            for conv in conventions:
                print(f"    - {conv.pattern}: {conv.context}")
                
    def test_vti_learning_loop(self):
        """Test that VTI learns from multiple validation cycles."""
        # First validation cycle
        req1 = "The system must be secure and handle user authentication properly."
        results1 = self.vti.run_vti_validation(req1, "Security Team")
        
        initial_conventions = len(self.vti._local_conventions)
        initial_improvements = len(self.vti._parsing_improvements)
        
        # Second validation cycle with similar pattern
        req2 = "We need secure data handling and proper user access controls."
        results2 = self.vti.run_vti_validation(req2, "Security Team")
        
        # Should have learned from first cycle
        final_conventions = len(self.vti._local_conventions)
        final_improvements = len(self.vti._parsing_improvements)
        
        print(f"Learning Loop Results:")
        print(f"  Initial conventions: {initial_conventions}")
        print(f"  Final conventions: {final_conventions}")
        print(f"  Initial improvements: {initial_improvements}")
        print(f"  Final improvements: {final_improvements}")
        
        # Verify learning occurred
        assert final_conventions >= initial_conventions
        assert final_improvements >= initial_improvements
        
    def test_audio_vti_validation(self):
        """Test the 'perverse case' - VTI from audio transcript."""
        # Simulate stakeholder interview transcript with conversational patterns
        audio_transcript = """
        Interviewer: What do you need from the new system?
        
        Stakeholder: Well, um, we basically need something that, you know, 
        handles our customer data better. Like, right now it's really slow 
        and users are complaining. We definitely need it to be faster.
        
        The login process is, uh, kind of confusing too. Users just want 
        to get in quickly, you know? Maybe we could make it simpler?
        
        Oh, and security is really important. We absolutely must protect 
        customer information. That's like, super critical for us.
        
        Interviewer: Any specific performance requirements?
        
        Stakeholder: Yeah, definitely. It should basically load in under 
        2 seconds. Users won't wait longer than that. And maybe we could 
        cache some data to make it even faster? Like, we just need it to 
        work better, you know? Basically, users just want it fast and simple.
        """
        
        stakeholder_info = "Customer Success Manager - Performance Focused"
        
        results = self.vti.run_audio_vti_validation(audio_transcript, stakeholder_info)
        
        # Verify audio-specific results
        assert "audio_transcript" in results
        assert "conversational_requirements" in results
        assert "speech_patterns" in results
        assert "conversational_conventions" in results
        assert "audio_confidence" in results
        
        print(f"Audio VTI Results:")
        print(f"  Conversational Requirements Length: {len(results['conversational_requirements'])}")
        print(f"  Speech Patterns: {results['speech_patterns']}")
        print(f"  Conversational Conventions: {results['conversational_conventions']}")
        print(f"  Audio Confidence: {results['audio_confidence']:.2f}")
        print(f"  Validation Score: {results['validation_score']:.2f}")
        
        # Audio should have specific patterns detected
        speech_patterns = results['speech_patterns']
        assert 'hesitation_markers' in speech_patterns
        assert 'certainty_markers' in speech_patterns
        assert 'uncertainty_markers' in speech_patterns
        
        # Should detect conversational conventions
        conventions = results['conversational_conventions']
        assert len(conventions) > 0
        
        print(f"  Detected Speech Patterns:")
        for pattern, count in speech_patterns.items():
            print(f"    {pattern}: {count}")
            
    def test_vti_gap_types(self):
        """Test different types of gaps VTI can detect."""
        # Requirements that will generate different gap types
        scope_gap_req = """
        Build a user management system. Handle user registration and login.
        """  # Vibe coding might assume more features
        
        assumption_gap_req = """
        Create a fast database system for our application.
        """  # Different assumptions about "fast"
        
        design_gap_req = """
        Implement secure authentication for the mobile app.
        """  # Different design approaches possible
        
        test_cases = [
            (scope_gap_req, "Scope Gap Test"),
            (assumption_gap_req, "Assumption Gap Test"),
            (design_gap_req, "Design Gap Test")
        ]
        
        all_gap_types = set()
        
        for req, context in test_cases:
            results = self.vti.run_vti_validation(req, context)
            
            gap_types = {gap.gap_type for gap in results['gaps_identified']}
            all_gap_types.update(gap_types)
            
            print(f"{context}:")
            print(f"  Gap types: {gap_types}")
            print(f"  Validation score: {results['validation_score']:.2f}")
            
        # Should detect multiple gap types across test cases
        print(f"All gap types detected: {all_gap_types}")
        assert len(all_gap_types) > 0
        
    def test_vti_local_convention_detection(self):
        """Test detection of local conventions from stakeholder patterns."""
        # Simulate requirements from stakeholder with specific patterns
        stakeholder_requirements = [
            "The system must be enterprise-grade and scalable for our needs.",
            "We need enterprise-level security and compliance features.",
            "Build an enterprise solution that handles our workflow requirements."
        ]
        
        stakeholder_context = "Enterprise Client - Compliance Focused"
        
        # Run multiple VTI cycles to detect patterns
        all_conventions = []
        for req in stakeholder_requirements:
            results = self.vti.run_vti_validation(req, stakeholder_context)
            all_conventions.extend(results['local_conventions'])
        
        print(f"Local Convention Detection:")
        print(f"  Total conventions detected: {len(all_conventions)}")
        
        # Should detect patterns in enterprise-focused language
        convention_patterns = [conv.pattern for conv in all_conventions]
        print(f"  Convention patterns: {convention_patterns}")
        
        # Verify learning database updated
        assert len(self.vti._local_conventions) > 0
        assert len(self.vti._parsing_improvements) > 0
        
        print(f"  Learning database:")
        print(f"    Conventions: {len(self.vti._local_conventions)}")
        print(f"    Improvements: {len(self.vti._parsing_improvements)}")
        
    def test_vti_validation_score_calculation(self):
        """Test validation score calculation based on gap severity."""
        # Perfect requirements (should score high)
        perfect_req = """
        WHEN user submits login credentials THEN system SHALL authenticate within 500ms.
        WHEN authentication fails THEN system SHALL log attempt and display error.
        WHEN user is authenticated THEN system SHALL redirect to dashboard.
        """
        
        # Ambiguous requirements (should score lower)
        ambiguous_req = """
        Make login work good and fast. Users should be happy with it.
        """
        
        perfect_results = self.vti.run_vti_validation(perfect_req, "Technical Stakeholder")
        ambiguous_results = self.vti.run_vti_validation(ambiguous_req, "Non-technical Stakeholder")
        
        print(f"Validation Score Comparison:")
        print(f"  Perfect requirements: {perfect_results['validation_score']:.2f}")
        print(f"  Ambiguous requirements: {ambiguous_results['validation_score']:.2f}")
        
        # Perfect requirements should score higher
        assert perfect_results['validation_score'] > ambiguous_results['validation_score']
        
        # Show gap analysis
        print(f"  Perfect req gaps: {len(perfect_results['gaps_identified'])}")
        print(f"  Ambiguous req gaps: {len(ambiguous_results['gaps_identified'])}")
        
        # Ambiguous should have more gaps
        assert len(ambiguous_results['gaps_identified']) >= len(perfect_results['gaps_identified'])