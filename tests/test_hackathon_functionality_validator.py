"""
Test suite for Hackathon Demo Framework functionality validator.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hackathon_demo_framework.validation.functionality_validator import CoreFunctionalityValidator


class TestCoreFunctionalityValidator:
    """Test suite for the core functionality validator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.project_path = Path(".")
        self.validator = CoreFunctionalityValidator(self.project_path)
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        assert self.validator.project_path == self.project_path
        assert len(self.validator.test_patterns) > 0
        assert len(self.validator.source_patterns) > 0
        assert len(self.validator.required_files) > 0
    
    @patch('subprocess.run')
    def test_functionality_gap_analysis(self, mock_subprocess):
        """Test functionality gap analysis."""
        # Mock successful test execution
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        gaps = self.validator.analyze_functionality_gaps()
        
        # Should return structured gap analysis
        assert "missing_tests" in gaps
        assert "incomplete_features" in gaps
        assert "broken_integrations" in gaps
        assert "missing_documentation" in gaps
        assert "performance_issues" in gaps
        
        # Should be lists
        assert isinstance(gaps["missing_tests"], list)
        assert isinstance(gaps["incomplete_features"], list)
        assert isinstance(gaps["broken_integrations"], list)
    
    def test_remediation_plan_generation(self):
        """Test remediation plan generation."""
        # Create sample gaps
        gaps = {
            "broken_integrations": ["Import error in module X"],
            "incomplete_features": ["Feature Y not implemented"],
            "missing_tests": ["No tests for module Z"],
            "missing_documentation": ["Missing API docs"],
            "performance_issues": ["Slow query in component A"]
        }
        
        remediation_plan = self.validator.generate_remediation_plan(gaps)
        
        # Should return prioritized list
        assert isinstance(remediation_plan, list)
        assert len(remediation_plan) > 0
        
        # Should prioritize critical issues first
        assert any("CRITICAL" in step for step in remediation_plan)
        assert any("HIGH" in step for step in remediation_plan)
        assert any("MEDIUM" in step for step in remediation_plan)
    
    def test_validation_result_structure(self):
        """Test that validation returns proper structure."""
        # Mock the validation method to return a known result
        with patch.object(self.validator, '_discover_and_run_tests') as mock_tests, \
             patch.object(self.validator, '_analyze_code_structure') as mock_structure, \
             patch.object(self.validator, '_check_documentation') as mock_docs, \
             patch.object(self.validator, '_validate_integrations') as mock_integrations, \
             patch.object(self.validator, '_assess_performance') as mock_performance:
            
            # Mock return values
            mock_tests.return_value = {"passed": 10, "failed": 0, "errors": []}
            mock_structure.return_value = {"score": 85, "issues": []}
            mock_docs.return_value = {"score": 80, "missing": []}
            mock_integrations.return_value = {"score": 90, "broken": []}
            mock_performance.return_value = {"score": 85, "issues": []}
            
            result = self.validator.validate_core_functionality()
            
            # Should return ValidationResult
            assert hasattr(result, 'is_valid')
            assert hasattr(result, 'score')
            assert hasattr(result, 'issues')
            assert hasattr(result, 'recommendations')
            
            # Score should be between 0 and 100
            assert 0 <= result.score <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])