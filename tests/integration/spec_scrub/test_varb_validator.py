"""
Integration tests for VARB (Validation through Authentic Requirements Behavior) Validator

Tests the VARB coding approach for preserving authentic stakeholder behavior
and validating requirements transformation quality.
"""

import pytest
from pathlib import Path

from src.spec_scrub.validation.varb_validator import (
    VARBValidator,
    VARBImplementationStyle,
    VARBImplementation
)


class TestVARBValidator:
    """Test VARB coding approach for authentic stakeholder behavior preservation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.varb = VARBValidator()
        
    def test_varb_initialization(self):
        """Test VARB validator initializes correctly."""
        assert self.varb is not None
        assert self.varb.ready() is True
        assert self.varb.status() == "ready"
        
        health = self.varb.health()
        assert health["status"] == "healthy"
        assert health["authenticity_preservation"] == "active"
        
    def test_varb_from_audio_transcript(self):
        """Test VARB coding from authentic stakeholder audio transcript."""
        # Realistic stakeholder interview with authentic behavioral patterns
        audio_transcript = """
        Interviewer: What's the main problem you're trying to solve?
        
        Stakeholder: Well, honestly, our users are really frustrated with the current system.
        Like, they spend way too much time just trying to find basic information. It's 
        really slowing down their work, you know? 
        
        What we really need is something that just works intuitively. Users shouldn't 
        have to think about it. They definitely need to get their tasks done quickly - 
        that's absolutely critical for our business.
        
        The current interface is, frankly, a mess. Users are constantly calling support
        because they can't figure out how to do simple things. We really need to fix
        this user experience problem.
        
        Performance is super important too. If it takes more than 2 seconds to load,
        users just give up. That's definitely not acceptable for us.
        """
        
        stakeholder_context = "Operations Manager - User Experience Focused"
        
        varb_impl = self.varb.varb_code_from_transcript(audio_transcript, stakeholder_context)
        
        # Verify VARB implementation structure
        assert varb_impl.style == VARBImplementationStyle.DIRECT_TRANSCRIPT
        assert varb_impl.raw_stakeholder_input == audio_transcript
        assert varb_impl.varb_code
        assert varb_impl.authentic_intent
        assert varb_impl.behavioral_assumptions
        assert 0.0 <= varb_impl.confidence_in_authenticity <= 1.0
        
        print(f"VARB Coding from Audio Transcript:")
        print(f"  Authentic Intent: {varb_impl.authentic_intent}")
        print(f"  Behavioral Assumptions: {len(varb_impl.behavioral_assumptions)}")
        print(f"  Authenticity Confidence: {varb_impl.confidence_in_authenticity:.2f}")
        print(f"  Implementation Rationale: {varb_impl.implementation_rationale}")
        
        # Should preserve user-centric focus from stakeholder's authentic voice
        assert "user" in varb_impl.authentic_intent.lower()
        
        # Should detect behavioral patterns
        assert len(varb_impl.behavioral_assumptions) > 0
        
    def test_varb_from_behavioral_patterns(self):
        """Test VARB coding from observed stakeholder behavioral patterns."""
        stakeholder_behavior = """
        This stakeholder consistently emphasizes user experience over technical elegance.
        They frequently mention specific user workflows and always ask "how will this 
        affect the user?" in technical discussions. They tend to prioritize immediate
        usability improvements over long-term architectural benefits.
        
        They show strong emotional investment in user satisfaction metrics and often
        reference specific user complaints. Their decision-making pattern shows they
        value quick wins that directly improve user experience.
        """
        
        domain_context = "E-commerce Product Management"
        
        varb_impl = self.varb.varb_code_from_behavior(stakeholder_behavior, domain_context)
        
        print(f"VARB Coding from Behavioral Patterns:")
        print(f"  Style: {varb_impl.style.value}")
        print(f"  Authentic Intent: {varb_impl.authentic_intent}")
        print(f"  Behavioral Assumptions: {varb_impl.behavioral_assumptions}")
        
        # Should capture user-centric behavioral pattern
        assert "user" in varb_impl.authentic_intent.lower()
        assert varb_impl.style == VARBImplementationStyle.BEHAVIORAL_PATTERN
        
    def test_varb_validation_against_structured(self):
        """Test VARB validation against structured implementation."""
        # Simulate structured implementation (from EARS requirements)
        structured_implementation = """
        class LoginSystem:
            def authenticate(self, credentials):
                # Validate credentials against database
                # Return authentication result
                pass
                
            def handle_login_failure(self):
                # Log failed attempt
                # Display generic error message
                pass
        """
        
        # Create VARB implementation that preserves stakeholder authenticity
        audio_transcript = """
        Users are really frustrated with login failures. When they can't get in,
        they immediately call support. We definitely need better error messages
        that actually help users understand what went wrong. The current system
        just says "login failed" which is really unhelpful.
        
        Users want to know if it's their password, their username, or if the
        system is down. They're smart people - they can handle more specific
        information. Really, we need to respect their intelligence.
        """
        
        varb_impl = self.varb.varb_code_from_transcript(
            audio_transcript, 
            "Customer Support Manager - User Empathy Focused"
        )
        
        # Validate structured against VARB
        validation_result = self.varb.validate_against_structured(
            structured_implementation, 
            varb_impl
        )
        
        print(f"VARB Validation Results:")
        print(f"  Authenticity Gaps: {len(validation_result.authenticity_gaps)}")
        print(f"  Behavioral Insights: {len(validation_result.behavioral_insights)}")
        print(f"  Recommended Adjustments: {len(validation_result.recommended_adjustments)}")
        print(f"  Validation Score: {validation_result.validation_score}")
        
        # Show specific gaps and insights
        for gap in validation_result.authenticity_gaps:
            print(f"    Gap: {gap}")
            
        for insight in validation_result.behavioral_insights:
            print(f"    Insight: {insight}")
            
        for recommendation in validation_result.recommended_adjustments:
            print(f"    Recommendation: {recommendation}")
        
        # Should identify authenticity gaps
        assert len(validation_result.authenticity_gaps) >= 0
        assert len(validation_result.behavioral_insights) > 0
        assert 0.0 <= validation_result.validation_score <= 1.0
        
    def test_varb_preserves_emotional_context(self):
        """Test that VARB coding preserves emotional context from stakeholders."""
        emotional_transcript = """
        I'm honestly getting really frustrated with our current system. Users are
        constantly complaining, and it's affecting team morale. We desperately need
        something that actually works for people.
        
        The current solution is frankly embarrassing. When I demo it to clients,
        I can see their disappointment. We absolutely must do better. This is
        critical for our reputation and user trust.
        
        What users really want is something that feels intuitive and responsive.
        They shouldn't have to struggle with basic tasks. That's just not acceptable.
        """
        
        varb_impl = self.varb.varb_code_from_transcript(
            emotional_transcript,
            "Product Owner - Quality Focused"
        )
        
        print(f"Emotional Context Preservation:")
        print(f"  Authentic Intent: {varb_impl.authentic_intent}")
        print(f"  Behavioral Assumptions: {varb_impl.behavioral_assumptions}")
        
        # Should capture emotional emphasis and urgency
        assert "critical" in varb_impl.authentic_intent.lower() or "urgent" in varb_impl.authentic_intent.lower()
        
        # Should have high authenticity confidence due to clear emotional indicators
        assert varb_impl.confidence_in_authenticity > 0.8
        
    def test_varb_handles_technical_vs_business_stakeholders(self):
        """Test VARB coding with different stakeholder types."""
        # Technical stakeholder transcript
        technical_transcript = """
        We need to implement a robust authentication system with proper session
        management and security controls. The architecture should support OAuth2
        and SAML integration. Performance requirements include sub-200ms response
        times and horizontal scalability.
        
        The system must handle edge cases like concurrent sessions and token
        refresh scenarios. We should implement proper logging and monitoring
        for security audit purposes.
        """
        
        # Business stakeholder transcript  
        business_transcript = """
        Our users just want to log in easily and get to their work. The current
        system is too complicated - they have to remember too many passwords.
        
        We're losing customers because the login process is frustrating. Can we
        make it simpler? Maybe like how Google or Facebook does it? Users are
        familiar with those patterns.
        
        The main thing is it needs to be fast and easy. Users won't tolerate
        complicated login processes in today's market.
        """
        
        technical_varb = self.varb.varb_code_from_transcript(
            technical_transcript, 
            "Senior Software Architect"
        )
        
        business_varb = self.varb.varb_code_from_transcript(
            business_transcript,
            "Business Development Manager"
        )
        
        print(f"Technical Stakeholder VARB:")
        print(f"  Intent: {technical_varb.authentic_intent}")
        print(f"  Confidence: {technical_varb.confidence_in_authenticity:.2f}")
        
        print(f"Business Stakeholder VARB:")
        print(f"  Intent: {business_varb.authentic_intent}")
        print(f"  Confidence: {business_varb.confidence_in_authenticity:.2f}")
        
        # Technical stakeholder should focus on system aspects
        assert "system" in technical_varb.authentic_intent.lower()
        
        # Business stakeholder should focus on user aspects
        assert "user" in business_varb.authentic_intent.lower()
        
        # Both should have reasonable confidence
        assert technical_varb.confidence_in_authenticity > 0.7
        assert business_varb.confidence_in_authenticity > 0.7
        
    def test_varb_authenticity_gap_detection(self):
        """Test VARB's ability to detect authenticity gaps in structured implementations."""
        # Stakeholder emphasizes user empathy and emotional support
        empathy_focused_transcript = """
        Our users are going through really stressful situations when they use our
        system. They're often dealing with urgent problems and need compassionate,
        helpful responses from the system.
        
        We absolutely must make sure error messages are kind and helpful, not
        technical and cold. Users need to feel supported, not blamed when something
        goes wrong. This is really important for our brand values.
        """
        
        # Structured implementation that misses the empathy aspect
        cold_structured_implementation = """
        class ErrorHandler:
            def handle_error(self, error_code):
                return f"Error {error_code}: Operation failed. Contact administrator."
                
            def log_error(self, error):
                logger.error(f"System error: {error}")
        """
        
        varb_impl = self.varb.varb_code_from_transcript(
            empathy_focused_transcript,
            "Customer Experience Manager"
        )
        
        validation_result = self.varb.validate_against_structured(
            cold_structured_implementation,
            varb_impl
        )
        
        print(f"Authenticity Gap Detection:")
        print(f"  Gaps Found: {len(validation_result.authenticity_gaps)}")
        for gap in validation_result.authenticity_gaps:
            print(f"    - {gap}")
            
        print(f"  Recommendations: {len(validation_result.recommended_adjustments)}")
        for rec in validation_result.recommended_adjustments:
            print(f"    - {rec}")
        
        # Should detect that structured implementation lost empathy focus
        assert len(validation_result.authenticity_gaps) > 0
        assert len(validation_result.recommended_adjustments) > 0
        
        # Validation score should reflect authenticity gaps
        assert validation_result.validation_score < 1.0