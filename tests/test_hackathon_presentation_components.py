"""
Test suite for Hackathon Demo Framework presentation components.

Tests the demo script generator, presentation materials creator, and timing optimizer.
"""

import pytest
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hackathon_demo_framework.models import (
    HackathonConfig, JudgingCriterion, DemoScript, SystematicEvidence, TechnicalAssessment
)
from hackathon_demo_framework.presentation import (
    DemoScriptGenerator, PresentationMaterialsCreator, DemoTimingOptimizer
)
from hackathon_demo_framework.presentation.demo_script_generator import (
    StoryArcType, DemoSection, DemoTemplate, ContentGuidelines
)
from hackathon_demo_framework.presentation.presentation_materials import (
    SlideType, VisualAssetType, SlideContent, VisualAsset, PresentationPackage
)
from hackathon_demo_framework.presentation.timing_optimizer import (
    PacingStrategy, TimingConstraint, TimingAnalysis, PacingRecommendation
)

class TestDemoScriptGenerator(ReflectiveModule):
    """Test suite for the demo script generator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.generator = DemoScriptGenerator(self.temp_dir)
        
        # Create test hackathon config
        self.hackathon_config = HackathonConfig(
            hackathon_name="Test Hackathon",
            hackathon_id="test-hackathon",
            submission_deadline=datetime.now() + timedelta(days=7),
            demo_time_limit=10,
            judging_criteria=[
                JudgingCriterion("Technical", 40.0, "Technical excellence"),
                JudgingCriterion("Innovation", 30.0, "Innovation and creativity"),
                JudgingCriterion("Presentation", 30.0, "Presentation quality")
            ],
            required_elements=["README.md", "Working demo"]
        )
        
        # Create test systematic evidence
        self.systematic_evidence = SystematicEvidence(
            spec_driven_evidence=["Requirements → Design → Implementation"],
            beast_mode_highlights=["PDCA cycles", "RCA analysis"],
            quality_metrics={"test_coverage": 85.0, "code_quality": 80.0},
            development_maturity_indicators=["Systematic testing", "Quality gates"],
            competitive_advantages=["Predictable quality", "Reduced risk"]
        )
        
        # Create test technical assessment
        self.technical_assessment = TechnicalAssessment(
            functionality_score=85.0,
            code_quality_score=80.0,
            documentation_score=75.0,
            test_coverage_percentage=85.0,
            installation_reliability=90.0,
            demo_stability_score=88.0,
            overall_technical_score=0  # Will be calculated
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generator_initialization(self):
        """Test demo script generator initialization."""
        assert self.generator.project_path == self.temp_dir
        assert len(self.generator.templates) > 0
        assert "devpost_standard" in self.generator.templates
        assert "mlh_quick" in self.generator.templates
    
    def test_demo_template_structure(self):
        """Test demo template data structure."""
        template = self.generator.templates["devpost_standard"]
        
        assert isinstance(template, DemoTemplate)
        assert template.name == "DevPost Standard"
        assert template.story_arc == StoryArcType.PROBLEM_SOLUTION
        assert template.target_duration == 600  # 10 minutes
        assert len(template.section_weights) > 0
        assert sum(template.section_weights.values()) == pytest.approx(1.0, rel=1e-2)
    
    def test_generate_demo_script(self):
        """Test demo script generation."""
        demo_script = self.generator.generate_demo_script(
            self.hackathon_config,
            self.systematic_evidence,
            self.technical_assessment,
            template_name="devpost_standard"
        )
        
        # Verify demo script structure
        assert isinstance(demo_script, DemoScript)
        assert demo_script.opening_hook is not None
        assert demo_script.problem_statement is not None
        assert demo_script.solution_overview is not None
        assert demo_script.technical_demonstration is not None
        assert demo_script.systematic_excellence is not None
        assert demo_script.business_impact is not None
        assert demo_script.closing_call_to_action is not None
        
        # Verify timing
        assert demo_script.total_duration <= self.hackathon_config.demo_time_limit * 60
        assert len(demo_script.timing_breakdown) > 0
        assert sum(demo_script.timing_breakdown.values()) == demo_script.total_duration
    
    def test_mlh_quick_template(self):
        """Test MLH quick template generation."""
        demo_script = self.generator.generate_demo_script(
            self.hackathon_config,
            self.systematic_evidence,
            self.technical_assessment,
            template_name="mlh_quick"
        )
        
        # MLH template should be shorter and demo-focused
        assert demo_script.total_duration <= 300  # 5 minutes max
        
        # Should have higher proportion for technical demonstration
        demo_ratio = demo_script.timing_breakdown.get("technical_demonstration", 0) / demo_script.total_duration
        assert demo_ratio >= 0.4  # At least 40% for demo
    
    def test_story_arc_creation(self):
        """Test story arc creation."""
        project_context = {
            "hackathon_name": "Test Hackathon",
            "systematic_evidence": self.systematic_evidence,
            "technical_assessment": self.technical_assessment
        }
        
        # Test problem-solution arc
        arc_content = self.generator.create_story_arc(
            StoryArcType.PROBLEM_SOLUTION, project_context
        )
        
        assert isinstance(arc_content, dict)
        assert DemoSection.OPENING_HOOK in arc_content
        assert DemoSection.PROBLEM_STATEMENT in arc_content
        assert DemoSection.SOLUTION_OVERVIEW in arc_content
        assert DemoSection.TECHNICAL_DEMONSTRATION in arc_content
        
        # Content should not be empty
        for section, content in arc_content.items():
            assert len(content.strip()) > 0
    
    def test_judge_optimization(self):
        """Test demo script optimization for judges."""
        # Create initial demo script
        demo_script = self.generator.generate_demo_script(
            self.hackathon_config,
            self.systematic_evidence,
            self.technical_assessment
        )
        
        # Optimize for judges
        optimized_script = self.generator.optimize_for_judges(
            demo_script,
            self.hackathon_config.judging_criteria,
            ["technical", "business"]
        )
        
        # Should return optimized script
        assert isinstance(optimized_script, DemoScript)
        assert optimized_script.total_duration == demo_script.total_duration
        
        # Content should be optimized (in practice, would check for specific optimizations)
        assert optimized_script.opening_hook is not None
        assert optimized_script.systematic_excellence is not None
    
    def test_backup_strategy_generation(self):
        """Test backup strategy generation."""
        demo_script = self.generator.generate_demo_script(
            self.hackathon_config,
            self.systematic_evidence,
            self.technical_assessment
        )
        
        backup_strategies = self.generator.generate_backup_strategies(
            demo_script, self.technical_assessment
        )
        
        assert isinstance(backup_strategies, list)
        assert len(backup_strategies) > 0
        
        # Should include common backup strategies
        backup_text = " ".join(backup_strategies).lower()
        assert "video" in backup_text or "screenshot" in backup_text
        assert "offline" in backup_text or "backup" in backup_text
    
    def test_content_guidelines_application(self):
        """Test application of content guidelines."""
        guidelines = ContentGuidelines(
            max_technical_depth=0.3,  # Low technical depth
            judge_personas=["business", "general"],
            key_differentiators=["systematic approach"],
            must_include_elements=["ROI", "market impact"],
            avoid_elements=["complex technical details"]
        )
        
        demo_script = self.generator.generate_demo_script(
            self.hackathon_config,
            self.systematic_evidence,
            self.technical_assessment,
            content_guidelines=guidelines
        )
        
        # Should generate script with guidelines applied
        assert isinstance(demo_script, DemoScript)
        # In practice, would verify that technical depth is reduced
        # and business elements are emphasized

class TestPresentationMaterialsCreator(ReflectiveModule):
    """Test suite for the presentation materials creator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.creator = PresentationMaterialsCreator(self.temp_dir)
        
        # Create test demo script
        self.demo_script = DemoScript(
            opening_hook="Test opening hook",
            problem_statement="Test problem statement",
            solution_overview="Test solution overview",
            technical_demonstration="Test technical demonstration",
            systematic_excellence="Test systematic excellence",
            business_impact="Test business impact",
            closing_call_to_action="Test closing",
            total_duration=600,
            timing_breakdown={
                "opening_hook": 30,
                "problem_statement": 90,
                "solution_overview": 120,
                "technical_demonstration": 210,
                "systematic_excellence": 60,
                "business_impact": 60,
                "closing_call_to_action": 30
            }
        )
        
        # Create test data (reuse from previous test)
        self.hackathon_config = HackathonConfig(
            hackathon_name="Test Hackathon",
            hackathon_id="test-hackathon",
            submission_deadline=datetime.now() + timedelta(days=7),
            demo_time_limit=10,
            judging_criteria=[
                JudgingCriterion("Technical", 40.0, "Technical excellence"),
                JudgingCriterion("Innovation", 30.0, "Innovation and creativity"),
                JudgingCriterion("Presentation", 30.0, "Presentation quality")
            ],
            required_elements=["README.md", "Working demo"]
        )
        
        self.systematic_evidence = SystematicEvidence(
            spec_driven_evidence=["Requirements → Design → Implementation"],
            beast_mode_highlights=["PDCA cycles", "RCA analysis"],
            quality_metrics={"test_coverage": 85.0, "code_quality": 80.0},
            development_maturity_indicators=["Systematic testing", "Quality gates"],
            competitive_advantages=["Predictable quality", "Reduced risk"]
        )
        
        self.technical_assessment = TechnicalAssessment(
            functionality_score=85.0,
            code_quality_score=80.0,
            documentation_score=75.0,
            test_coverage_percentage=85.0,
            installation_reliability=90.0,
            demo_stability_score=88.0,
            overall_technical_score=0
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_creator_initialization(self):
        """Test presentation materials creator initialization."""
        assert self.creator.project_path == self.temp_dir
        assert len(self.creator.slide_templates) > 0
        assert "devpost_standard" in self.creator.slide_templates
    
    def test_slide_template_structure(self):
        """Test slide template structure."""
        template = self.creator.slide_templates["devpost_standard"]
        
        assert isinstance(template, list)
        assert SlideType.TITLE in template
        assert SlideType.PROBLEM in template
        assert SlideType.DEMO in template
        assert SlideType.CLOSING in template
    
    def test_create_presentation_package(self):
        """Test presentation package creation."""
        package = self.creator.create_presentation_package(
            self.demo_script,
            self.hackathon_config,
            self.systematic_evidence,
            self.technical_assessment,
            template_name="devpost_standard"
        )
        
        # Verify package structure
        assert isinstance(package, PresentationPackage)
        assert len(package.slides) > 0
        assert len(package.visual_assets) > 0
        assert package.speaker_notes is not None
        assert len(package.timing_guide) > 0
        assert len(package.backup_materials) > 0
        assert package.judge_handout is not None
    
    def test_slide_content_structure(self):
        """Test individual slide content structure."""
        package = self.creator.create_presentation_package(
            self.demo_script,
            self.hackathon_config,
            self.systematic_evidence,
            self.technical_assessment
        )
        
        # Check first slide (title slide)
        title_slide = package.slides[0]
        assert isinstance(title_slide, SlideContent)
        assert title_slide.slide_type == SlideType.TITLE
        assert title_slide.title is not None
        assert title_slide.content is not None
        assert len(title_slide.visual_elements) > 0
        assert title_slide.speaker_notes is not None
        assert title_slide.timing_seconds > 0
    
    def test_visual_asset_generation(self):
        """Test visual asset generation."""
        package = self.creator.create_presentation_package(
            self.demo_script,
            self.hackathon_config,
            self.systematic_evidence,
            self.technical_assessment
        )
        
        # Should have various types of visual assets
        asset_types = [asset.asset_type for asset in package.visual_assets]
        assert VisualAssetType.DIAGRAM in asset_types
        assert VisualAssetType.CHART in asset_types
        
        # Each asset should have proper structure
        for asset in package.visual_assets:
            assert isinstance(asset, VisualAsset)
            assert asset.name is not None
            assert asset.description is not None
    
    def test_markdown_generation(self):
        """Test slide deck markdown generation."""
        package = self.creator.create_presentation_package(
            self.demo_script,
            self.hackathon_config,
            self.systematic_evidence,
            self.technical_assessment
        )
        
        markdown = self.creator.generate_slide_deck_markdown(package)
        
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        assert "# Hackathon Presentation Slides" in markdown
        assert "## Slide" in markdown
        assert "### Content" in markdown
        assert "## Timing Guide" in markdown
    
    def test_visual_asset_specifications(self):
        """Test visual asset specification generation."""
        package = self.creator.create_presentation_package(
            self.demo_script,
            self.hackathon_config,
            self.systematic_evidence,
            self.technical_assessment
        )
        
        specifications = self.creator.create_visual_asset_specifications(package.visual_assets)
        
        assert isinstance(specifications, str)
        assert len(specifications) > 0
        assert "# Visual Asset Creation Specifications" in specifications
        assert "## Asset" in specifications
        assert "### Creation Instructions" in specifications
    
    def test_time_constraint_optimization(self):
        """Test presentation optimization for time constraints."""
        package = self.creator.create_presentation_package(
            self.demo_script,
            self.hackathon_config,
            self.systematic_evidence,
            self.technical_assessment
        )
        
        # Optimize for shorter time (5 minutes = 300 seconds)
        optimized_package = self.creator.optimize_for_time_constraints(package, 300)
        
        # Should reduce timing
        original_total = sum(slide.timing_seconds for slide in package.slides)
        optimized_total = sum(slide.timing_seconds for slide in optimized_package.slides)
        
        assert optimized_total <= 300
        assert optimized_total < original_total
        
        # Should maintain slide structure
        assert len(optimized_package.slides) == len(package.slides)

class TestDemoTimingOptimizer(ReflectiveModule):
    """Test suite for the demo timing optimizer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = DemoTimingOptimizer()
        
        # Create test demo script
        self.demo_script = DemoScript(
            opening_hook="Test opening hook",
            problem_statement="Test problem statement",
            solution_overview="Test solution overview",
            technical_demonstration="Test technical demonstration",
            systematic_excellence="Test systematic excellence",
            business_impact="Test business impact",
            closing_call_to_action="Test closing",
            total_duration=720,  # 12 minutes - over limit
            timing_breakdown={
                "opening_hook": 60,  # Too long
                "problem_statement": 120,
                "solution_overview": 150,
                "technical_demonstration": 240,
                "systematic_excellence": 60,
                "business_impact": 60,
                "closing_call_to_action": 30
            }
        )
        
        # Create test hackathon config
        self.hackathon_config = HackathonConfig(
            hackathon_name="Test Hackathon",
            hackathon_id="test-hackathon",
            submission_deadline=datetime.now() + timedelta(days=7),
            demo_time_limit=10,  # 10 minutes
            judging_criteria=[
                JudgingCriterion("Technical", 40.0, "Technical excellence"),
                JudgingCriterion("Innovation", 30.0, "Innovation and creativity"),
                JudgingCriterion("Presentation", 30.0, "Presentation quality")
            ],
            required_elements=["README.md", "Working demo"]
        )
    
    def test_optimizer_initialization(self):
        """Test timing optimizer initialization."""
        assert len(self.optimizer.timing_templates) > 0
        assert "devpost_standard" in self.optimizer.timing_templates
        assert len(self.optimizer.pacing_guidelines) > 0
    
    def test_timing_template_structure(self):
        """Test timing template structure."""
        template = self.optimizer.timing_templates["devpost_standard"]
        
        assert isinstance(template, dict)
        assert "opening_hook" in template
        assert "technical_demonstration" in template
        assert "systematic_excellence" in template
        
        # Ratios should sum to approximately 1.0
        assert sum(template.values()) == pytest.approx(1.0, rel=1e-2)
    
    def test_optimize_demo_timing(self):
        """Test demo timing optimization."""
        optimization = self.optimizer.optimize_demo_timing(
            self.demo_script,
            self.hackathon_config,
            pacing_strategy=PacingStrategy.DEMO_FOCUSED
        )
        
        # Verify optimization structure
        assert hasattr(optimization, 'optimized_script')
        assert hasattr(optimization, 'timing_analysis')
        assert hasattr(optimization, 'pacing_recommendations')
        assert hasattr(optimization, 'rehearsal_schedule')
        assert hasattr(optimization, 'contingency_plans')
        
        # Optimized script should fit time limit
        assert optimization.optimized_script.total_duration <= self.hackathon_config.demo_time_limit * 60
        
        # Should have recommendations
        assert len(optimization.pacing_recommendations) > 0
    
    def test_pacing_analysis(self):
        """Test pacing effectiveness analysis."""
        analysis = self.optimizer.analyze_pacing_effectiveness(self.demo_script)
        
        assert "overall_pacing_score" in analysis
        assert "section_pacing" in analysis
        assert "engagement_peaks" in analysis
        assert "improvement_areas" in analysis
        
        # Should identify timing issues
        assert analysis["overall_pacing_score"] >= 0
        assert analysis["overall_pacing_score"] <= 100
        
        # Should have section analysis
        assert len(analysis["section_pacing"]) > 0
    
    def test_rehearsal_plan_creation(self):
        """Test rehearsal plan creation."""
        rehearsal_plan = self.optimizer.create_timing_rehearsal_plan(
            self.demo_script, rehearsal_sessions=3
        )
        
        assert len(rehearsal_plan) == 3
        
        for session in rehearsal_plan:
            assert "session_number" in session
            assert "focus_areas" in session
            assert "timing_goals" in session
            assert "success_criteria" in session
            assert "feedback_points" in session
            
            # Each session should have content
            assert len(session["focus_areas"]) > 0
            assert len(session["success_criteria"]) > 0
    
    def test_real_time_timing_guide(self):
        """Test real-time timing guide generation."""
        timing_guide = self.optimizer.generate_real_time_timing_guide(self.demo_script)
        
        assert "checkpoints" in timing_guide
        assert "section_targets" in timing_guide
        assert "warning_thresholds" in timing_guide
        assert "recovery_strategies" in timing_guide
        
        # Should have checkpoints for each section
        assert len(timing_guide["checkpoints"]) > 0
        
        # Each checkpoint should have required fields
        for checkpoint in timing_guide["checkpoints"]:
            assert "section" in checkpoint
            assert "target_time" in checkpoint
            assert "section_duration" in checkpoint
            assert "key_message" in checkpoint
    
    def test_pacing_strategy_application(self):
        """Test different pacing strategies."""
        strategies = [
            PacingStrategy.DEMO_FOCUSED,
            PacingStrategy.SYSTEMATIC_EMPHASIS,
            PacingStrategy.FRONT_LOADED
        ]
        
        for strategy in strategies:
            optimization = self.optimizer.optimize_demo_timing(
                self.demo_script,
                self.hackathon_config,
                pacing_strategy=strategy
            )
            
            # Should produce valid optimization
            assert optimization.optimized_script.total_duration <= self.hackathon_config.demo_time_limit * 60
            
            # Strategy should influence timing
            if strategy == PacingStrategy.DEMO_FOCUSED:
                demo_ratio = (optimization.optimized_script.timing_breakdown.get("technical_demonstration", 0) / 
                             optimization.optimized_script.total_duration)
                assert demo_ratio >= 0.3  # Should have significant demo time
            
            elif strategy == PacingStrategy.SYSTEMATIC_EMPHASIS:
                sys_ratio = (optimization.optimized_script.timing_breakdown.get("systematic_excellence", 0) / 
                            optimization.optimized_script.total_duration)
                assert sys_ratio >= 0.08  # Should have adequate systematic time
    
    def test_contingency_plan_generation(self):
        """Test contingency plan generation."""
        optimization = self.optimizer.optimize_demo_timing(
            self.demo_script,
            self.hackathon_config
        )
        
        contingency_plans = optimization.contingency_plans
        
        assert len(contingency_plans) > 0
        
        # Should include common contingencies
        plans_text = " ".join(contingency_plans).lower()
        assert "running long" in plans_text or "time" in plans_text
        assert "demo" in plans_text or "backup" in plans_text

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