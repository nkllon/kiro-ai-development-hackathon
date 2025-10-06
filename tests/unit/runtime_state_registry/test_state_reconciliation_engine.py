#!/usr/bin/env python3
"""
Test Suite for State Reconciliation Engine
==========================================

Comprehensive tests for the Phase 2 State Reconciliation Engine implementation.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import json

from src.runtime_state_registry.reconciliation.state_reconciliation_engine import (
    StateReconciliationEngine, ReconciliationStrategy, ReconciliationResult
)
from src.runtime_state_registry.core.models import DriftSeverity, ConfigurationDrift


class TestStateReconciliationEngine:
    """Test suite for StateReconciliationEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create a StateReconciliationEngine instance for testing."""
        return StateReconciliationEngine(
            reconciliation_strategy=ReconciliationStrategy.HIERARCHICAL,
            compliance_threshold=0.8,
            auto_remediation_enabled=False
        )
    
    @pytest.fixture
    def mock_service_states(self):
        """Mock service state data for testing."""
        return {
            "spec_state": {
                "version": "1.0.0",
                "port": 8080,
                "replicas": 3
            },
            "cms_state": {
                "version": "1.0.1",
                "port": 8080,
                "replicas": 2
            },
            "runtime_state": {
                "version": "1.0.0",
                "port": 8080,
                "replicas": 2,
                "status": "running"
            }
        }
    
    def test_initialization(self):
        """Test StateReconciliationEngine initialization."""
        engine = StateReconciliationEngine(
            reconciliation_strategy=ReconciliationStrategy.SPEC_AUTHORITY,
            compliance_threshold=0.9,
            auto_remediation_enabled=True
        )
        
        assert engine.reconciliation_strategy == ReconciliationStrategy.SPEC_AUTHORITY
        assert engine.compliance_threshold == 0.9
        assert engine.auto_remediation_enabled is True
        assert engine.last_reconciliation is None
        assert len(engine.reconciliation_history) == 0
        assert len(engine.compliance_trends) == 0
    
    @pytest.mark.asyncio
    async def test_reconcile_service_state_success(self, engine, mock_service_states):
        """Test successful service state reconciliation."""
        # Mock collector methods
        with patch.object(engine, '_collect_spec_state', return_value=mock_service_states["spec_state"]), \
             patch.object(engine, '_collect_cms_state', return_value=mock_service_states["cms_state"]), \
             patch.object(engine, '_collect_runtime_state', return_value=mock_service_states["runtime_state"]):
            
            result = await engine.reconcile_service_state("test_service")
            
            assert isinstance(result, ReconciliationResult)
            assert result.service_name == "test_service"
            assert result.compliance_score > 0.0
            assert result.drift_severity in [DriftSeverity.LOW, DriftSeverity.MEDIUM, DriftSeverity.HIGH]
            assert len(result.conflicts_detected) >= 0
            assert len(result.authority_chain) >= 0
    
    @pytest.mark.asyncio
    async def test_reconcile_service_state_error_handling(self, engine):
        """Test error handling in service state reconciliation."""
        # Mock collector methods to raise exceptions
        with patch.object(engine, '_collect_spec_state', side_effect=Exception("Test error")):
            
            result = await engine.reconcile_service_state("test_service")
            
            assert isinstance(result, ReconciliationResult)
            assert result.service_name == "test_service"
            assert result.compliance_score == 0.0
            assert result.drift_severity == DriftSeverity.CRITICAL
            assert len(result.conflicts_detected) > 0
            assert "error" in result.authority_chain
    
    @pytest.mark.asyncio
    async def test_reconcile_all_services(self, engine):
        """Test reconciliation of all services."""
        # Mock service discovery
        with patch.object(engine, '_discover_all_services', return_value={"service1", "service2"}), \
             patch.object(engine, 'reconcile_service_state') as mock_reconcile:
            
            # Mock reconcile_service_state to return test results
            mock_reconcile.return_value = ReconciliationResult(
                service_name="test",
                reconciliation_timestamp=datetime.now(),
                compliance_score=0.8,
                drift_severity=DriftSeverity.LOW,
                conflicts_detected=[],
                conflicts_resolved=[],
                remediation_actions=[],
                authority_chain=["spec"]
            )
            
            results = await engine.reconcile_all_services()
            
            assert len(results) == 2
            assert "service1" in results
            assert "service2" in results
            assert mock_reconcile.call_count == 2
    
    def test_get_compliance_summary_no_data(self, engine):
        """Test compliance summary with no data."""
        summary = engine.get_compliance_summary()
        
        assert summary["status"] == "no_data"
        assert "message" in summary
    
    def test_get_compliance_summary_with_data(self, engine):
        """Test compliance summary with historical data."""
        # Add some test data
        test_result = ReconciliationResult(
            service_name="test_service",
            reconciliation_timestamp=datetime.now(),
            compliance_score=0.85,
            drift_severity=DriftSeverity.LOW,
            conflicts_detected=[],
            conflicts_resolved=[],
            remediation_actions=[],
            authority_chain=["spec"]
        )
        
        engine.reconciliation_history.append(test_result)
        engine.last_reconciliation = datetime.now()
        
        summary = engine.get_compliance_summary()
        
        assert summary["status"] in ["healthy", "degraded"]
        assert summary["total_services"] == 1
        assert summary["average_compliance"] == 0.85
        assert summary["compliance_threshold"] == 0.8
        assert "drift_severity_distribution" in summary
        assert "compliance_trend" in summary
    
    def test_detect_conflicts(self, engine):
        """Test conflict detection between state layers."""
        spec_state = {"version": "1.0.0", "port": 8080}
        cms_state = {"version": "1.0.1", "port": 8080}
        runtime_state = {"version": "1.0.0", "port": 8081}
        
        conflicts = engine._detect_conflicts("test_service", spec_state, cms_state, runtime_state)
        
        assert len(conflicts) > 0
        # Should detect version mismatch between spec and cms
        # Should detect port mismatch between cms and runtime
    
    def test_compare_states(self, engine):
        """Test state comparison logic."""
        state1 = {"key1": "value1", "key2": "value2"}
        state2 = {"key1": "value1", "key3": "value3"}
        
        conflicts = engine._compare_states("layer1", "layer2", state1, state2)
        
        assert len(conflicts) == 2  # key2 missing in layer2, key3 missing in layer1
        
        # Test value mismatch
        state3 = {"key1": "different_value"}
        conflicts = engine._compare_states("layer1", "layer2", state1, state3)
        
        assert len(conflicts) >= 1  # Should detect value mismatch for key1
    
    def test_resolve_conflicts_hierarchical(self, engine):
        """Test conflict resolution with hierarchical strategy."""
        conflicts = [
            ConfigurationDrift(
                service_name="test",
                drift_type="spec_cms_mismatch",
                severity=DriftSeverity.MEDIUM,
                description="Test conflict",
                expected_value="spec_value",
                actual_value="cms_value",
                remediation_suggestion="Fix it"
            )
        ]
        
        resolved, authority_chain = engine._resolve_conflicts(conflicts)
        
        assert len(resolved) == len(conflicts)
        assert len(authority_chain) == len(conflicts)
        assert "spec" in authority_chain  # Hierarchical should prefer spec
    
    def test_calculate_compliance_score(self, engine):
        """Test compliance score calculation."""
        # Test with no conflicts
        score = engine._calculate_compliance_score("test", {}, {}, {}, [])
        assert score == 0.0  # No state data
        
        # Test with conflicts
        conflicts = [
            ConfigurationDrift(
                service_name="test",
                drift_type="test",
                severity=DriftSeverity.LOW,
                description="Test",
                expected_value="a",
                actual_value="b",
                remediation_suggestion="Fix"
            )
        ]
        
        score = engine._calculate_compliance_score("test", {"key": "value"}, {}, {}, conflicts)
        assert 0.0 <= score <= 1.0
    
    def test_classify_drift_severity(self, engine):
        """Test drift severity classification."""
        # Test critical compliance
        severity = engine._classify_drift_severity([], 0.2)
        assert severity == DriftSeverity.CRITICAL
        
        # Test high drift
        severity = engine._classify_drift_severity([], 0.5)
        assert severity == DriftSeverity.HIGH
        
        # Test medium drift
        severity = engine._classify_drift_severity([], 0.7)
        assert severity == DriftSeverity.MEDIUM
        
        # Test low drift
        severity = engine._classify_drift_severity([], 0.9)
        assert severity == DriftSeverity.LOW
    
    def test_generate_remediation_actions(self, engine):
        """Test remediation action generation."""
        conflicts = [
            ConfigurationDrift(
                service_name="test",
                drift_type="configuration_mismatch",
                severity=DriftSeverity.HIGH,
                description="Config mismatch",
                expected_value="expected",
                actual_value="actual",
                remediation_suggestion="Fix config"
            )
        ]
        
        actions = engine._generate_remediation_actions(
            "test_service", conflicts, conflicts, DriftSeverity.HIGH
        )
        
        assert len(actions) > 0
        assert all("action_type" in action for action in actions)
        assert all("priority" in action for action in actions)
        assert all("description" in action for action in actions)
    
    def test_update_compliance_trends(self, engine):
        """Test compliance trend tracking."""
        service_name = "test_service"
        timestamp = datetime.now()
        score = 0.85
        
        engine._update_compliance_trends(service_name, score, timestamp)
        
        assert service_name in engine.compliance_trends
        assert len(engine.compliance_trends[service_name]) == 1
        assert engine.compliance_trends[service_name][0] == (timestamp, score)
    
    def test_calculate_compliance_trend(self, engine):
        """Test compliance trend calculation."""
        # Add test data
        now = datetime.now()
        old_time = now - timedelta(hours=13)
        recent_time = now - timedelta(hours=1)
        
        engine.compliance_trends["service1"] = [
            (old_time, 0.6),
            (recent_time, 0.8)
        ]
        
        trend = engine._calculate_compliance_trend()
        assert trend in ["improving", "degrading", "stable"]
    
    def test_get_capabilities(self, engine):
        """Test capabilities reporting."""
        capabilities = engine.get_capabilities()
        
        assert capabilities["module_type"] == "state_reconciliation_engine"
        assert "reconciliation_strategies" in capabilities
        assert "current_strategy" in capabilities
        assert "compliance_threshold" in capabilities
        assert "features" in capabilities
    
    def test_get_module_info(self, engine):
        """Test module info reporting."""
        info = engine.get_module_info()
        
        assert info["name"] == "StateReconciliationEngine"
        assert "version" in info
        assert "status" in info
        assert "total_reconciliations" in info
    
    def test_graceful_degradation(self, engine):
        """Test graceful degradation handling."""
        test_error = Exception("Test error")
        degradation_info = engine.graceful_degradation(test_error)
        
        assert degradation_info["status"] == "degraded"
        assert degradation_info["error"] == str(test_error)
        assert "available_functions" in degradation_info
        assert "degraded_functions" in degradation_info
        assert "recovery_actions" in degradation_info


class TestReconciliationStrategies:
    """Test different reconciliation strategies."""
    
    @pytest.mark.parametrize("strategy", [
        ReconciliationStrategy.SPEC_AUTHORITY,
        ReconciliationStrategy.CMS_AUTHORITY,
        ReconciliationStrategy.RUNTIME_REALITY,
        ReconciliationStrategy.HIERARCHICAL
    ])
    def test_reconciliation_strategies(self, strategy):
        """Test different reconciliation strategies."""
        engine = StateReconciliationEngine(reconciliation_strategy=strategy)
        
        conflicts = [
            ConfigurationDrift(
                service_name="test",
                drift_type="spec_cms_mismatch",
                severity=DriftSeverity.MEDIUM,
                description="Test conflict",
                expected_value="spec_value",
                actual_value="cms_value",
                remediation_suggestion="Fix it"
            )
        ]
        
        resolved, authority_chain = engine._resolve_conflicts(conflicts)
        
        assert len(resolved) == len(conflicts)
        assert len(authority_chain) == len(conflicts)
        
        # Check authority chain matches strategy
        if strategy == ReconciliationStrategy.SPEC_AUTHORITY:
            assert all("spec" in auth for auth in authority_chain)
        elif strategy == ReconciliationStrategy.CMS_AUTHORITY:
            assert all("cms" in auth for auth in authority_chain)
        elif strategy == ReconciliationStrategy.RUNTIME_REALITY:
            assert all("runtime" in auth for auth in authority_chain)


class TestReconciliationResult:
    """Test ReconciliationResult data class."""
    
    def test_reconciliation_result_creation(self):
        """Test ReconciliationResult creation and serialization."""
        result = ReconciliationResult(
            service_name="test_service",
            reconciliation_timestamp=datetime.now(),
            compliance_score=0.85,
            drift_severity=DriftSeverity.LOW,
            conflicts_detected=[],
            conflicts_resolved=[],
            remediation_actions=[{"action": "test"}],
            authority_chain=["spec", "cms"]
        )
        
        assert result.service_name == "test_service"
        assert result.compliance_score == 0.85
        assert result.drift_severity == DriftSeverity.LOW
        
        # Test serialization
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["service_name"] == "test_service"
        assert result_dict["compliance_score"] == 0.85
        assert result_dict["drift_severity"] == "low"
        assert "reconciliation_timestamp" in result_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])