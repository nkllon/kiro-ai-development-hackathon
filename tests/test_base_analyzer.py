"""Unit tests for base analyzer functionality."""

import pytest
from unittest.mock import Mock

from src.visual_diagram_validation.analyzers.base_analyzer import (
    BaseQualityAnalyzer, ViolationBuilder, RecommendationBuilder
)
from src.visual_diagram_validation.core.models import (
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    PNGImage, Severity, ActionType, BoundingBox
)


class TestAnalyzer(BaseQualityAnalyzer, ReflectiveModule):
    """Test implementation of BaseQualityAnalyzer."""
    
    @property
    def analyzer_name(self) -> str:
        return "test_analyzer"
    
    @property
    def supported_rules(self) -> list[str]:
        return ["test_rule_1", "test_rule_2"]
    
    def _perform_analysis(self, image, metadata):
        """Test analysis that adds a violation."""
        if image.width < 800:
            self.add_violation(
                rule_id="min_width",
                severity=Severity.WARNING,
                current_value=image.width,
                expected_value=800,
                description=f"Image width {image.width} is below minimum 800px"
            )


class TestBaseQualityAnalyzer(ReflectiveModule):
    """Test base analyzer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = TestAnalyzer()
        self.test_image = PNGImage(
            data=b"fake_png_data",
            width=600,  # Below minimum for test
            height=400,
            dpi=300,
            color_mode="RGB"
        )
    
    def test_analyzer_properties(self):
        """Test analyzer properties."""
        assert self.analyzer.analyzer_name == "test_analyzer"
        assert "test_rule_1" in self.analyzer.supported_rules
        assert "test_rule_2" in self.analyzer.supported_rules
    
    def test_analyze_basic(self):
        """Test basic analysis functionality."""
        result = self.analyzer.analyze(self.test_image)
        
        assert result.analyzer_name == "test_analyzer"
        assert len(result.violations) == 1
        assert len(result.recommendations) == 1
        assert result.processing_time > 0
        
        # Check violation details
        violation = result.violations[0]
        assert violation.rule_id == "min_width"
        assert violation.severity == Severity.WARNING
        assert violation.current_value == 600
        assert violation.expected_value == 800
    
    def test_analyze_with_metadata(self):
        """Test analysis with metadata."""
        metadata = {"source": "test", "format": "svg"}
        
        result = self.analyzer.analyze(self.test_image, metadata)
        
        assert "config" in result.metadata
        assert "image_size" in result.metadata
        assert result.metadata["image_size"] == "600x400"
    
    def test_add_violation(self):
        """Test adding violations."""
        bbox = BoundingBox(x=10, y=20, width=100, height=50)
        
        self.analyzer.add_violation(
            rule_id="test_rule",
            severity=Severity.ERROR,
            current_value=2.1,
            expected_value=4.5,
            description="Test violation",
            location=bbox,
            category="accessibility"
        )
        
        assert len(self.analyzer.violations) == 1
        violation = self.analyzer.violations[0]
        assert violation.rule_id == "test_rule"
        assert violation.severity == Severity.ERROR
        assert violation.location == bbox
        assert violation.category == "accessibility"
    
    def test_add_recommendation(self):
        """Test adding recommendations."""
        self.analyzer.add_recommendation(
            violation_id="test_violation",
            action_type=ActionType.INCREASE,
            guidance="Increase contrast ratio",
            outcome="Better accessibility",
            priority=1
        )
        
        assert len(self.analyzer.recommendations) == 1
        rec = self.analyzer.recommendations[0]
        assert rec.action_type == ActionType.INCREASE
        assert rec.priority == 1
    
    def test_get_threshold_with_config(self):
        """Test threshold retrieval with configuration."""
        config = {"contrast_threshold": 4.5, "font_size_threshold": 12}
        analyzer = TestAnalyzer(config)
        
        assert analyzer.get_threshold("contrast", 3.0) == 4.5
        assert analyzer.get_threshold("font_size", 10) == 12
        assert analyzer.get_threshold("unknown", 5.0) == 5.0
    
    def test_is_rule_enabled(self):
        """Test rule enablement checking."""
        config = {"enable_contrast_check": True, "enable_color_check": False}
        analyzer = TestAnalyzer(config)
        
        assert analyzer.is_rule_enabled("contrast_check") is True
        assert analyzer.is_rule_enabled("color_check") is False
        assert analyzer.is_rule_enabled("unknown_check") is True  # Default
    
    def test_get_severity_for_deviation(self):
        """Test severity determination based on deviation."""
        assert self.analyzer.get_severity_for_deviation(60) == Severity.ERROR
        assert self.analyzer.get_severity_for_deviation(30) == Severity.WARNING
        assert self.analyzer.get_severity_for_deviation(10) == Severity.INFO
    
    def test_analysis_error_handling(self):
        """Test error handling during analysis."""
        class FailingAnalyzer(BaseQualityAnalyzer, ReflectiveModule):
            @property
            def analyzer_name(self):
                return "failing_analyzer"
            
            @property
            def supported_rules(self):
                return ["fail_rule"]
            
            def _perform_analysis(self, image, metadata):
                raise ValueError("Simulated analysis failure")
        
        analyzer = FailingAnalyzer()
        result = analyzer.analyze(self.test_image)
        
        # Should have error violation
        assert len(result.violations) == 1
        assert result.violations[0].severity == Severity.ERROR
        assert "Analysis failed" in result.violations[0].description
    
    def test_recommendation_generation(self):
        """Test automatic recommendation generation."""
        # Add violation that should generate recommendation
        self.analyzer.add_violation(
            rule_id="low_contrast",
            severity=Severity.WARNING,
            current_value=2.1,
            expected_value=4.5,
            description="Contrast too low"
        )
        
        self.analyzer._generate_recommendations()
        
        assert len(self.analyzer.recommendations) == 1
        rec = self.analyzer.recommendations[0]
        assert rec.action_type == ActionType.INCREASE
        assert "2.1" in rec.specific_guidance
        assert "4.5" in rec.specific_guidance


class TestViolationBuilder(ReflectiveModule):
    """Test violation builder pattern."""
    
    def test_basic_build(self):
        """Test basic violation building."""
        violation = (ViolationBuilder("test_rule")
                    .with_severity(Severity.ERROR)
                    .with_values(2.0, 4.0)
                    .with_description("Test description")
                    .build())
        
        assert violation.rule_id == "test_rule"
        assert violation.severity == Severity.ERROR
        assert violation.current_value == 2.0
        assert violation.expected_value == 4.0
        assert violation.description == "Test description"
    
    def test_with_location_and_category(self):
        """Test building with location and category."""
        bbox = BoundingBox(x=10, y=20, width=100, height=50)
        
        violation = (ViolationBuilder("test_rule")
                    .with_location(bbox)
                    .with_category("accessibility")
                    .build())
        
        assert violation.location == bbox
        assert violation.category == "accessibility"


class TestRecommendationBuilder(ReflectiveModule):
    """Test recommendation builder pattern."""
    
    def test_basic_build(self):
        """Test basic recommendation building."""
        rec = (RecommendationBuilder("violation_123")
               .with_action(ActionType.INCREASE)
               .with_guidance("Increase font size")
               .with_outcome("Better readability")
               .with_priority(1)
               .build())
        
        assert rec.violation_id == "violation_123"
        assert rec.action_type == ActionType.INCREASE
        assert rec.specific_guidance == "Increase font size"
        assert rec.expected_outcome == "Better readability"

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

        assert rec.priority == 1