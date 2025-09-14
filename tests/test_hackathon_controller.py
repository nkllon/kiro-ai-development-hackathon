"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:24:55.831477
"""


import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hackathon_demo_framework import (
    HackathonDemoController,
    HackathonConfig,
    JudgingCriterion,
    DemoPackage,
    DemoScript,
    JudgeMaterials
)
from hackathon_demo_framework.models import (
from src.rm_ddd.core.base_reflective_module import ReflectiveModule, ModuleCapability, ModuleStatus, ModuleHealth

    TechnicalAssessment,
    ComplianceAssessment
)


class TestHackathonDemoController(ReflectiveModule):
    """Test suite for the hackathon demo controller."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.project_path = Path(".")
        self.test_config = HackathonConfig(
            hackathon_name="Test Hackathon",
            hackathon_id="test-hackathon",
            submission_deadline=datetime.now() + timedelta(days=7),
            demo_time_limit=10,
            judging_criteria=[
                JudgingCriterion("Technical", 40.0, "Technical excellence"),
                JudgingCriterion("Innovation", 30.0, "Innovation and creativity"),
                JudgingCriterion("Presentation", 30.0, "Presentation quality")
            ],
            required_elements=["README.md", ".kiro directory", "Working demo"]
        )
        self.controller = HackathonDemoController(self.project_path, self.test_config)
    
    def test_controller_initialization(self):
        """Test that the demo controller initializes correctly."""
        assert self.controller.project_path == self.project_path
        assert self.controller.config.hackathon_name == "Test Hackathon"
        assert len(self.controller.validation_gates) == 5
    
    def test_hackathon_templates(self):
        """Test predefined hackathon templates."""
        templates = self.controller.get_hackathon_templates()
        
        assert "devpost" in templates
        assert "mlh" in templates
        
        devpost_template = templates["devpost"]
        assert devpost_template.hackathon_name == "DevPost Hackathon"
        assert devpost_template.demo_time_limit == 10
        
        mlh_template = templates["mlh"]
        assert mlh_template.hackathon_name == "MLH Hackathon"
        assert mlh_template.demo_time_limit == 5  # MLH typically shorter
    
    def test_template_customization(self):
        """Test hackathon template customization."""
        customizations = {
            "hackathon_name": "Custom Hackathon",
            "demo_time_limit": 8,
            "submission_deadline": datetime.now() + timedelta(days=3)
        }
        
        custom_config = self.controller.customize_hackathon_config("devpost", customizations)
        
        assert custom_config.hackathon_name == "Custom Hackathon"
        assert custom_config.demo_time_limit == 8
        assert custom_config.submission_deadline == customizations["submission_deadline"]
        
        # Should preserve other template values
        assert len(custom_config.judging_criteria) > 0
        assert len(custom_config.required_elements) > 0
    
    def test_judge_package_generation(self):
        """Test judge evaluation package generation."""
        # Create a minimal demo package
        demo_package = DemoPackage(
            demo_script=DemoScript(
                opening_hook="Test", problem_statement="Test", solution_overview="Test",
                technical_demonstration="Test", systematic_excellence="Test",
                business_impact="Test", closing_call_to_action="Test", total_duration=0
            ),
            judge_materials=JudgeMaterials(
                executive_summary="Executive Summary", technical_overview="Technical Overview",
                systematic_development_evidence="Systematic Evidence", competitive_analysis="Competitive Analysis",
                business_impact_summary="Business Impact", demo_instructions="Demo Instructions"
            ),
            demo_environment=self.controller._prepare_demo_environment(),
            systematic_evidence=self.controller._collect_systematic_evidence(),
            technical_assessment=TechnicalAssessment(
                functionality_score=85.0, code_quality_score=80.0, documentation_score=75.0,
                test_coverage_percentage=85.0, installation_reliability=90.0,
                demo_stability_score=88.0, overall_technical_score=0
            ),
            compliance_assessment=ComplianceAssessment(
                mandatory_requirements={"README.md": True}, hackathon_specific_criteria={},
                submission_format_compliance=True, deadline_compliance=True,
                team_eligibility=True, overall_compliance_score=0
            )
        )
        
        judge_package = self.controller.generate_judge_package(demo_package)
        
        # Verify judge package structure
        assert "executive_summary" in judge_package
        assert "quick_start_guide" in judge_package
        assert "demo_script" in judge_package
        assert "technical_highlights" in judge_package
        assert "systematic_excellence" in judge_package
        assert "compliance_status" in judge_package
        assert "demo_reliability" in judge_package
        
        # Verify technical highlights
        tech_highlights = judge_package["technical_highlights"]
        assert "score" in tech_highlights
        assert "test_coverage" in tech_highlights
        assert "key_features" in tech_highlights
    
    def test_demo_rehearsal_execution(self):
        """Test demo rehearsal execution and timing analysis."""
        demo_package = DemoPackage(
            demo_script=DemoScript(
                opening_hook="Test opening", problem_statement="Test problem",
                solution_overview="Test solution", technical_demonstration="Test demo",
                systematic_excellence="Test systematic", business_impact="Test impact",
                closing_call_to_action="Test closing", total_duration=0
            ),
            judge_materials=JudgeMaterials(
                executive_summary="Test", technical_overview="Test",
                systematic_development_evidence="Test", competitive_analysis="Test",
                business_impact_summary="Test", demo_instructions="Test"
            ),
            demo_environment=self.controller._prepare_demo_environment(),
            systematic_evidence=self.controller._collect_systematic_evidence(),
            technical_assessment=TechnicalAssessment(
                functionality_score=85.0, code_quality_score=80.0, documentation_score=75.0,
                test_coverage_percentage=85.0, installation_reliability=90.0,
                demo_stability_score=88.0, overall_technical_score=0
            ),
            compliance_assessment=ComplianceAssessment(
                mandatory_requirements={"README.md": True}, hackathon_specific_criteria={},
                submission_format_compliance=True, deadline_compliance=True,
                team_eligibility=True, overall_compliance_score=0
            )
        )
        
        rehearsal_results = self.controller.execute_demo_rehearsal(demo_package)
        
        # Verify rehearsal results structure
        assert "start_time" in rehearsal_results
        assert "end_time" in rehearsal_results
        assert "sections" in rehearsal_results
        assert "total_duration" in rehearsal_results
        assert "issues" in rehearsal_results
        assert "suggestions" in rehearsal_results
        
        # Verify section analysis
        sections = rehearsal_results["sections"]
        assert "opening_hook" in sections
        assert "problem_statement" in sections
        assert "technical_demonstration" in sections
        
        # Each section should have timing analysis
        for section_name, section_data in sections.items():
            assert "target_duration" in section_data
            assert "actual_duration" in section_data
            assert "variance" in section_data


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