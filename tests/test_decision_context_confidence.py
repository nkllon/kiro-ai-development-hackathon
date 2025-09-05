"""
Unit tests for DecisionContext confidence score functionality
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any, List

# Import all DecisionContext classes
from src.beast_mode.orchestration.tool_orchestration_engine import DecisionContext as OrchestrationDecisionContext
from src.beast_mode.ghostbusters.enhanced_multi_perspective_validator import DecisionContext as ValidatorDecisionContext
from src.beast_mode.documentation.adr_system import DecisionContext as ADRDecisionContext


class TestOrchestrationDecisionContext:
    """Test DecisionContext from tool orchestration engine"""
    
    def test_decision_context_has_confidence_score_attribute(self):
        """Test that DecisionContext has confidence_score attribute"""
        context = OrchestrationDecisionContext(
            decision_id="test-001",
            problem_statement="Test problem",
            available_options=["option1", "option2"],
            constraints=["constraint1"],
            stakeholder_requirements={"req1": "value1"},
            time_pressure="normal",
            risk_tolerance="medium"
        )
        
        # Should have confidence_score attribute with default value 0.0
        assert hasattr(context, 'confidence_score')
        assert context.confidence_score == 0.0
        assert isinstance(context.confidence_score, float)
    
    def test_decision_context_confidence_score_initialization(self):
        """Test that confidence_score can be initialized with custom value"""
        context = OrchestrationDecisionContext(
            decision_id="test-002",
            problem_statement="Test problem",
            available_options=["option1"],
            constraints=[],
            stakeholder_requirements={},
            time_pressure="urgent",
            risk_tolerance="low",
            confidence_score=0.85
        )
        
        assert context.confidence_score == 0.85
    
    def test_calculate_confidence_method_exists(self):
        """Test that calculate_confidence method exists and works"""
        context = OrchestrationDecisionContext(
            decision_id="test-003",
            problem_statement="Test problem",
            available_options=["option1"],
            constraints=[],
            stakeholder_requirements={},
            time_pressure="normal",
            risk_tolerance="medium",
            confidence_score=0.75
        )
        
        # Should have calculate_confidence method
        assert hasattr(context, 'calculate_confidence')
        assert callable(context.calculate_confidence)
        
        # Should return the confidence_score value
        calculated_confidence = context.calculate_confidence()
        assert calculated_confidence == 0.75
        assert isinstance(calculated_confidence, float)
    
    def test_confidence_score_range_validation(self):
        """Test that confidence_score accepts valid range values"""
        # Test minimum value
        context_min = OrchestrationDecisionContext(
            decision_id="test-004",
            problem_statement="Test problem",
            available_options=["option1"],
            constraints=[],
            stakeholder_requirements={},
            time_pressure="normal",
            risk_tolerance="medium",
            confidence_score=0.0
        )
        assert context_min.confidence_score == 0.0
        
        # Test maximum value
        context_max = OrchestrationDecisionContext(
            decision_id="test-005",
            problem_statement="Test problem",
            available_options=["option1"],
            constraints=[],
            stakeholder_requirements={},
            time_pressure="normal",
            risk_tolerance="medium",
            confidence_score=1.0
        )
        assert context_max.confidence_score == 1.0
        
        # Test mid-range value
        context_mid = OrchestrationDecisionContext(
            decision_id="test-006",
            problem_statement="Test problem",
            available_options=["option1"],
            constraints=[],
            stakeholder_requirements={},
            time_pressure="normal",
            risk_tolerance="medium",
            confidence_score=0.5
        )
        assert context_mid.confidence_score == 0.5


class TestValidatorDecisionContext:
    """Test DecisionContext from enhanced multi-perspective validator"""
    
    def test_validator_decision_context_has_confidence_score(self):
        """Test that validator DecisionContext has confidence_score attribute"""
        context = ValidatorDecisionContext(
            decision_id="validator-001",
            decision_description="Test validator decision",
            decision_type="technical",
            context_data={"key": "value"},
            constraints=["constraint1"],
            success_criteria=["criteria1"],
            risk_factors=["risk1"],
            time_pressure="medium",
            impact_scope="module"
        )
        
        assert hasattr(context, 'confidence_score')
        assert context.confidence_score == 0.0
        assert hasattr(context, 'calculate_confidence')
        assert context.calculate_confidence() == 0.0
    
    def test_validator_confidence_score_custom_value(self):
        """Test validator DecisionContext with custom confidence score"""
        context = ValidatorDecisionContext(
            decision_id="validator-002",
            decision_description="Test validator decision",
            decision_type="architectural",
            context_data={},
            constraints=[],
            success_criteria=[],
            risk_factors=[],
            time_pressure="high",
            impact_scope="system",
            confidence_score=0.9
        )
        
        assert context.confidence_score == 0.9
        assert context.calculate_confidence() == 0.9


class TestADRDecisionContext:
    """Test DecisionContext from ADR system"""
    
    def test_adr_decision_context_has_confidence_score(self):
        """Test that ADR DecisionContext has confidence_score attribute"""
        context = ADRDecisionContext(
            problem_statement="Test ADR problem",
            business_drivers=["driver1"],
            technical_constraints=["constraint1"],
            stakeholders=["stakeholder1"],
            timeline="Q1 2024"
        )
        
        assert hasattr(context, 'confidence_score')
        assert context.confidence_score == 0.0
        assert hasattr(context, 'calculate_confidence')
        assert context.calculate_confidence() == 0.0
    
    def test_adr_confidence_score_with_risk_factors(self):
        """Test ADR DecisionContext with risk factors and confidence score"""
        context = ADRDecisionContext(
            problem_statement="Complex ADR decision",
            business_drivers=["cost_reduction", "performance"],
            technical_constraints=["legacy_system", "budget"],
            stakeholders=["engineering", "product", "business"],
            timeline="Q2 2024",
            risk_factors=["technical_debt", "resource_constraints"],
            confidence_score=0.65
        )
        
        assert context.confidence_score == 0.65
        assert context.calculate_confidence() == 0.65
        assert len(context.risk_factors) == 2


class TestDecisionContextIntegration:
    """Integration tests for DecisionContext confidence functionality"""
    
    def test_all_decision_contexts_have_consistent_interface(self):
        """Test that all DecisionContext classes have consistent confidence interface"""
        contexts = [
            OrchestrationDecisionContext(
                decision_id="integration-001",
                problem_statement="Test",
                available_options=["opt1"],
                constraints=[],
                stakeholder_requirements={},
                time_pressure="normal",
                risk_tolerance="medium"
            ),
            ValidatorDecisionContext(
                decision_id="integration-002",
                decision_description="Test",
                decision_type="technical",
                context_data={},
                constraints=[],
                success_criteria=[],
                risk_factors=[],
                time_pressure="medium",
                impact_scope="module"
            ),
            ADRDecisionContext(
                problem_statement="Test",
                business_drivers=[],
                technical_constraints=[],
                stakeholders=[],
                timeline="Q1"
            )
        ]
        
        for context in contexts:
            # All should have confidence_score attribute
            assert hasattr(context, 'confidence_score')
            assert isinstance(context.confidence_score, float)
            assert context.confidence_score == 0.0
            
            # All should have calculate_confidence method
            assert hasattr(context, 'calculate_confidence')
            assert callable(context.calculate_confidence)
            assert context.calculate_confidence() == 0.0
    
    def test_confidence_score_modification(self):
        """Test that confidence_score can be modified after initialization"""
        context = OrchestrationDecisionContext(
            decision_id="modify-001",
            problem_statement="Test modification",
            available_options=["opt1"],
            constraints=[],
            stakeholder_requirements={},
            time_pressure="normal",
            risk_tolerance="medium"
        )
        
        # Initial value
        assert context.confidence_score == 0.0
        
        # Modify confidence score
        context.confidence_score = 0.8
        assert context.confidence_score == 0.8
        assert context.calculate_confidence() == 0.8
        
        # Modify again
        context.confidence_score = 0.3
        assert context.confidence_score == 0.3
        assert context.calculate_confidence() == 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])