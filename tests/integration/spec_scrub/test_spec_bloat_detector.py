#!/usr/bin/env python3
"""
Integration tests for SpecBloatDetector - testing the detector on itself.
The ultimate recursive perversity: can our theater detector detect its own theater?
"""

import pytest
from pathlib import Path
from src.spec_scrub.validation.spec_bloat_detector import SpecBloatDetector, TheaterPatternType


class TestSpecBloatDetector:
    """Test the bloat detector by having it analyze itself and known perverse cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = SpecBloatDetector()
        self.repo_root = Path(__file__).parent.parent.parent.parent
        self.specs_dir = self.repo_root / ".kiro" / "specs"
    
    def test_detect_perverse_case_theater(self):
        """Test detection on the known perverse case."""
        perverse_spec = self.specs_dir / "rmi-rm-ddd-conformance-remediation"
        
        if not perverse_spec.exists():
            pytest.skip("Perverse case spec not found")
        
        # Calculate bloat score
        bloat_score = self.detector.calculate_bloat_score(str(perverse_spec))
        
        # Should detect massive theater
        assert bloat_score > 5.0, f"Expected massive bloat, got {bloat_score}"
        
        # Detect patterns
        patterns = self.detector.detect_theater_patterns(str(perverse_spec))
        
        # Should detect multiple theater patterns
        assert len(patterns) >= 3, f"Expected multiple patterns, got {len(patterns)}"
        
        # Should detect over-engineering
        over_engineering = [p for p in patterns if p.pattern_type == TheaterPatternType.OVER_ENGINEERING]
        assert len(over_engineering) > 0, "Should detect over-engineering pattern"
    
    def test_detect_self_theater(self):
        """Test the detector on our own spec - the recursive perversity test."""
        our_spec = self.specs_dir / "spec-theater-remediation"
        
        if not our_spec.exists():
            pytest.skip("Our own spec not found")
        
        # Calculate bloat score
        bloat_score = self.detector.calculate_bloat_score(str(our_spec))
        
        # Our spec should be focused (low bloat)
        assert bloat_score < 2.0, f"Our own spec is bloated! Score: {bloat_score}"
        
        # Detect patterns
        patterns = self.detector.detect_theater_patterns(str(our_spec))
        
        # Should detect format impedance (EARS vs Beast Mode)
        format_issues = [p for p in patterns if p.pattern_type == TheaterPatternType.FORMAT_IMPEDANCE]
        assert len(format_issues) > 0, "Should detect format impedance in our own spec"
    
    def test_mathematical_validation(self):
        """Test the mathematical foundations of bloat detection."""
        # Test bloat score calculation
        test_spec = self.specs_dir / "spec-theater-remediation"
        
        if not test_spec.exists():
            pytest.skip("Test spec not found")
        
        metrics = self.detector._extract_spec_metrics(str(test_spec))
        
        # Validate metrics extraction
        assert metrics.requirements_count >= 0
        assert metrics.design_elements_count >= 0
        assert metrics.implementation_tasks_count >= 0
        assert 0.0 <= metrics.coverage_ratio <= 2.0
        assert 0.0 <= metrics.format_compatibility_score <= 1.0
    
    def test_decomposition_suggestions(self):
        """Test decomposition suggestions for bloated specs."""
        perverse_spec = self.specs_dir / "rmi-rm-ddd-conformance-remediation"
        
        if not perverse_spec.exists():
            pytest.skip("Perverse case spec not found")
        
        decomposition_plan = self.detector.suggest_decomposition(str(perverse_spec))
        
        # Should provide actionable recommendations
        assert "recommendations" in decomposition_plan
        assert len(decomposition_plan["recommendations"]) > 0
        
        # Should include specific actions
        actions = [rec["action"] for rec in decomposition_plan["recommendations"]]
        expected_actions = ["decompose_requirements", "simplify_design", "add_implementation_tasks"]
        
        # Should suggest at least one of these actions
        assert any(action in actions for action in expected_actions)
    
    def test_reflective_module_compliance(self):
        """Test that the detector properly implements ReflectiveModule interface."""
        # Test health monitoring
        assert self.detector.is_healthy() == True
        
        # Test status reporting
        status = self.detector.get_module_status()
        assert "module_name" in status
        assert status["status"] == "operational"
        
        # Test health indicators
        health = self.detector.get_health_indicators()
        assert "detector_operational" in health
        assert health["detector_operational"] == True
        
        # Test primary responsibility
        responsibility = self.detector._get_primary_responsibility()
        assert "theater" in responsibility.lower()
    
    def test_enemy_is_us_detection(self):
        """
        The ultimate test: Can we detect that we are our own enemy?
        
        This test validates that our detector can identify when we've created
        the very problems we're trying to solve.
        """
        # Test both specs
        perverse_spec = self.specs_dir / "rmi-rm-ddd-conformance-remediation"
        our_spec = self.specs_dir / "spec-theater-remediation"
        
        if not (perverse_spec.exists() and our_spec.exists()):
            pytest.skip("Required specs not found for enemy detection test")
        
        # Analyze both
        perverse_patterns = self.detector.detect_theater_patterns(str(perverse_spec))
        our_patterns = self.detector.detect_theater_patterns(str(our_spec))
        
        # The perverse case should have more theater patterns
        assert len(perverse_patterns) > len(our_patterns), "Perverse case should be worse than our spec"
        
        # But we should still detect some issues in our own spec (format impedance)
        assert len(our_patterns) > 0, "We should detect that we are part of the problem"
        
        # Specifically, we should detect format impedance in our own spec
        our_format_issues = [p for p in our_patterns if p.pattern_type == TheaterPatternType.FORMAT_IMPEDANCE]
        assert len(our_format_issues) > 0, "We have met the enemy and he are us - format impedance detected"