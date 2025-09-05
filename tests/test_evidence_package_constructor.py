"""
Test evidence package constructor functionality
Tests for Task 5.1: Update EvidencePackage dataclass constructor
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from beast_mode.assessment.evidence_package_generator import SuperiorityEvidence


class TestEvidencePackageConstructor:
    """Test evidence package constructor with concrete_proof parameter"""
    
    def test_superiority_evidence_with_concrete_proof(self):
        """Test SuperiorityEvidence initialization with concrete_proof parameter"""
        concrete_proof_text = "Measured 3.2x improvement in tool health management"
        
        evidence = SuperiorityEvidence(
            metric_name="Tool Health Management",
            beast_mode_value=95.0,
            adhoc_value=60.0,
            improvement_ratio=3.2,
            improvement_percentage=220.0,
            evidence_type="reliability",
            statistical_confidence=3.5,
            concrete_proof=concrete_proof_text
        )
        
        assert evidence.concrete_proof == concrete_proof_text
        assert evidence.metric_name == "Tool Health Management"
        assert evidence.beast_mode_value == 95.0
        assert evidence.adhoc_value == 60.0
        assert evidence.improvement_ratio == 3.2
        assert evidence.improvement_percentage == 220.0
        assert evidence.evidence_type == "reliability"
        assert evidence.statistical_confidence == 3.5
    
    def test_superiority_evidence_without_concrete_proof(self):
        """Test SuperiorityEvidence initialization without concrete_proof parameter"""
        evidence = SuperiorityEvidence(
            metric_name="Decision Making Accuracy",
            beast_mode_value=85.0,
            adhoc_value=45.0,
            improvement_ratio=1.89,
            improvement_percentage=89.0,
            evidence_type="quality",
            statistical_confidence=3.0
        )
        
        # Should have default concrete_proof from __post_init__
        assert evidence.concrete_proof is not None
        assert "Decision Making Accuracy" in evidence.concrete_proof
        assert "89.0% improvement demonstrated" in evidence.concrete_proof
        assert evidence.metric_name == "Decision Making Accuracy"
        assert evidence.beast_mode_value == 85.0
        assert evidence.adhoc_value == 45.0
    
    def test_superiority_evidence_concrete_proof_none_initialization(self):
        """Test SuperiorityEvidence initialization with concrete_proof=None"""
        evidence = SuperiorityEvidence(
            metric_name="Performance Optimization",
            beast_mode_value=350.0,
            adhoc_value=750.0,
            improvement_ratio=2.14,
            improvement_percentage=53.3,
            evidence_type="performance",
            statistical_confidence=3.2,
            concrete_proof=None
        )
        
        # Should have default concrete_proof from __post_init__
        assert evidence.concrete_proof is not None
        assert "Performance Optimization" in evidence.concrete_proof
        assert "53.3% improvement demonstrated" in evidence.concrete_proof
    
    def test_superiority_evidence_post_init_method(self):
        """Test that __post_init__ method properly initializes concrete_proof"""
        evidence = SuperiorityEvidence(
            metric_name="Test Metric",
            beast_mode_value=100.0,
            adhoc_value=50.0,
            improvement_ratio=2.0,
            improvement_percentage=100.0,
            evidence_type="test",
            statistical_confidence=2.5
        )
        
        # Verify __post_init__ was called and set concrete_proof
        expected_proof = "Evidence for Test Metric: 100.0% improvement demonstrated"
        assert evidence.concrete_proof == expected_proof
    
    def test_superiority_evidence_all_parameters(self):
        """Test SuperiorityEvidence with all parameters including concrete_proof"""
        evidence = SuperiorityEvidence(
            metric_name="Comprehensive Test",
            beast_mode_value=200.0,
            adhoc_value=100.0,
            improvement_ratio=2.0,
            improvement_percentage=100.0,
            evidence_type="comprehensive",
            statistical_confidence=4.0,
            concrete_proof="Custom concrete proof text"
        )
        
        # Verify all parameters are set correctly
        assert evidence.metric_name == "Comprehensive Test"
        assert evidence.beast_mode_value == 200.0
        assert evidence.adhoc_value == 100.0
        assert evidence.improvement_ratio == 2.0
        assert evidence.improvement_percentage == 100.0
        assert evidence.evidence_type == "comprehensive"
        assert evidence.statistical_confidence == 4.0
        assert evidence.concrete_proof == "Custom concrete proof text"
    
    def test_superiority_evidence_dataclass_behavior(self):
        """Test that SuperiorityEvidence behaves correctly as a dataclass"""
        evidence1 = SuperiorityEvidence(
            metric_name="Test",
            beast_mode_value=100.0,
            adhoc_value=50.0,
            improvement_ratio=2.0,
            improvement_percentage=100.0,
            evidence_type="test",
            statistical_confidence=3.0,
            concrete_proof="Test proof"
        )
        
        evidence2 = SuperiorityEvidence(
            metric_name="Test",
            beast_mode_value=100.0,
            adhoc_value=50.0,
            improvement_ratio=2.0,
            improvement_percentage=100.0,
            evidence_type="test",
            statistical_confidence=3.0,
            concrete_proof="Test proof"
        )
        
        # Test equality (dataclass should implement __eq__)
        assert evidence1 == evidence2
        
        # Test string representation
        assert "SuperiorityEvidence" in str(evidence1)
        assert "Test" in str(evidence1)