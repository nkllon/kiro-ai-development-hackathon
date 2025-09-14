"""
Test suite for Hackathon Demo Framework models.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hackathon_demo_framework import (
    HackathonConfig,
    JudgingCriterion,
    DemoPackage,
    DemoScript,
    JudgeMaterials
)
from hackathon_demo_framework.models import (
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    ValidationResult,
    TechnicalAssessment,
    ComplianceAssessment
)


class TestHackathonModels(ReflectiveModule):
    """Test suite for hackathon demo framework models."""
    
    def test_hackathon_config_validation(self):
        """Test hackathon configuration validation."""
        # Test valid configuration
        config = HackathonConfig(
            hackathon_name="Valid Hackathon",
            hackathon_id="valid-hackathon",
            submission_deadline=datetime.now() + timedelta(days=1),
            demo_time_limit=5,
            judging_criteria=[
                JudgingCriterion("Technical", 50.0, "Technical merit"),
                JudgingCriterion("Business", 50.0, "Business value")
            ],
            required_elements=["README.md"]
        )
        assert config.hackathon_name == "Valid Hackathon"
        
        # Test invalid configuration - weights don't sum to 100
        with pytest.raises(ValueError, match="must sum to 100%"):
            HackathonConfig(
                hackathon_name="Invalid Hackathon",
                hackathon_id="invalid-hackathon",
                submission_deadline=datetime.now() + timedelta(days=1),
                demo_time_limit=5,
                judging_criteria=[
                    JudgingCriterion("Technical", 30.0, "Technical merit"),
                    JudgingCriterion("Business", 30.0, "Business value")  # Only 60% total
                ],
                required_elements=["README.md"]
            )
    
    def test_demo_script_generation(self):
        """Test demo script structure and timing."""
        demo_script = DemoScript(
            opening_hook="Test opening",
            problem_statement="Test problem",
            solution_overview="Test solution",
            technical_demonstration="Test demo",
            systematic_excellence="Test systematic",
            business_impact="Test impact",
            closing_call_to_action="Test closing",
            total_duration=0  # Will be calculated
        )
        
        # Check that timing is calculated correctly
        assert demo_script.total_duration == 510  # Sum of default timings
        assert "opening_hook" in demo_script.timing_breakdown
        assert demo_script.timing_breakdown["opening_hook"] == 30
    
    def test_technical_assessment_calculation(self):
        """Test technical assessment score calculation."""
        assessment = TechnicalAssessment(
            functionality_score=85.0,
            code_quality_score=80.0,
            documentation_score=75.0,
            test_coverage_percentage=90.0,
            installation_reliability=95.0,
            demo_stability_score=88.0,
            overall_technical_score=0  # Will be calculated
        )
        
        # Check that overall score is calculated
        assert assessment.overall_technical_score > 0
        assert 80 <= assessment.overall_technical_score <= 90  # Should be in this range
    
    def test_compliance_assessment_calculation(self):
        """Test compliance assessment score calculation."""
        assessment = ComplianceAssessment(
            mandatory_requirements={"README.md": True, ".kiro": True, "tests": False},
            hackathon_specific_criteria={"theme": 85.0, "tech_req": 90.0},
            submission_format_compliance=True,
            deadline_compliance=True,
            team_eligibility=True,
            overall_compliance_score=0  # Will be calculated
        )
        
        # Check that score is calculated based on requirements
        assert assessment.overall_compliance_score > 0
        # Should be penalized for missing tests requirement
        assert assessment.overall_compliance_score < 100
    
    def test_demo_package_readiness(self):
        """Test demo package readiness assessment."""
        # Create a demo package with good scores
        demo_package = DemoPackage(
            demo_script=DemoScript(
                opening_hook="Test", problem_statement="Test", solution_overview="Test",
                technical_demonstration="Test", systematic_excellence="Test",
                business_impact="Test", closing_call_to_action="Test", total_duration=0
            ),
            judge_materials=JudgeMaterials(
                executive_summary="Test", technical_overview="Test",
                systematic_development_evidence="Test", competitive_analysis="Test",
                business_impact_summary="Test", demo_instructions="Test"
            ),
            demo_environment=type('MockEnv', (), {'reliability_score': 90.0})(),
            systematic_evidence=None,
            technical_assessment=TechnicalAssessment(
                functionality_score=85.0, code_quality_score=85.0, documentation_score=85.0,
                test_coverage_percentage=85.0, installation_reliability=90.0,
                demo_stability_score=90.0, overall_technical_score=0
            ),
            compliance_assessment=ComplianceAssessment(
                mandatory_requirements={"README.md": True, ".kiro": True},
                hackathon_specific_criteria={}, submission_format_compliance=True,
                deadline_compliance=True, team_eligibility=True, overall_compliance_score=0
            )
        )
        
        # Check readiness assessment
        readiness_score = demo_package.get_readiness_score()
        assert readiness_score > 80  # Should be ready with good scores
        
        # Test submission readiness
        is_ready = demo_package.is_submission_ready()
        assert is_ready  # Should be ready with these scores
    
    def test_validation_result_structure(self):
        """Test validation result structure and logic."""
        # Test successful validation
        success_result = ValidationResult(
            is_valid=True,
            score=95.0,
            issues=[],
            recommendations=[]
        )
        assert success_result.is_valid
        assert success_result.score == 95.0
        
        # Test failed validation
        failure_result = ValidationResult(
            is_valid=False,
            score=65.0,
            issues=["Test coverage too low", "Missing documentation"],
            recommendations=["Add more tests", "Improve documentation"]
        )
        assert not failure_result.is_valid
        assert len(failure_result.issues) == 2
        assert len(failure_result.recommendations) == 2


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