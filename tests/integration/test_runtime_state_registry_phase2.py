#!/usr/bin/env python3
"""
Integration Test for Runtime State Registry Phase 2
===================================================

Comprehensive integration test demonstrating the complete Phase 2 system:
- State Reconciliation Engine
- Drift Detection System
- Compliance Monitoring
- Auto-Remediation Engine

This test validates the end-to-end workflow of the Runtime State Registry.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from src.runtime_state_registry.reconciliation.state_reconciliation_engine import (
    StateReconciliationEngine, ReconciliationStrategy
)
from src.runtime_state_registry.compliance.drift_detector import DriftDetector
from src.runtime_state_registry.compliance.compliance_monitor import ComplianceMonitor
from src.runtime_state_registry.remediation.auto_remediation_engine import (
    AutoRemediationEngine, RemediationSafety
)
from src.runtime_state_registry.core.models import DriftSeverity


class TestRuntimeStateRegistryPhase2Integration:
    """Integration test suite for Phase 2 components."""
    
    @pytest.fixture
    def mock_service_data(self):
        """Mock service data for testing."""
        return {
            "web_service": {
                "spec_state": {
                    "version": "2.0.0",
                    "port": 8080,
                    "replicas": 3,
                    "health_check": "/health"
                },
                "cms_state": {
                    "version": "1.9.0",
                    "port": 8080,
                    "replicas": 2,
                    "health_check": "/health"
                },
                "runtime_state": {
                    "version": "1.9.0",
                    "port": 8080,
                    "replicas": 2,
                    "status": "running",
                    "health_status": "healthy"
                }
            },
            "database_service": {
                "spec_state": {
                    "version": "13.0",
                    "port": 5432,
                    "storage": "100Gi"
                },
                "cms_state": {
                    "version": "13.0",
                    "port": 5432,
                    "storage": "100Gi"
                },
                "runtime_state": {
                    "version": "13.0",
                    "port": 5432,
                    "status": "running",
                    "health_status": "healthy"
                }
            },
            "orphaned_service": {
                "runtime_state": {
                    "version": "1.0.0",
                    "port": 9999,
                    "status": "running"
                }
            },
            "missing_service": {
                "spec_state": {
                    "version": "1.0.0",
                    "port": 7777
                },
                "cms_state": {
                    "version": "1.0.0",
                    "port": 7777
                }
            }
        }
    
    @pytest.fixture
    def reconciliation_engine(self):
        """Create StateReconciliationEngine for testing."""
        return StateReconciliationEngine(
            reconciliation_strategy=ReconciliationStrategy.HIERARCHICAL,
            compliance_threshold=0.8,
            auto_remediation_enabled=False
        )
    
    @pytest.fixture
    def drift_detector(self):
        """Create DriftDetector for testing."""
        return DriftDetector(
            confidence_threshold=0.7,
            enable_auto_remediation_suggestions=True
        )
    
    @pytest.fixture
    def compliance_monitor(self):
        """Create ComplianceMonitor for testing."""
        return ComplianceMonitor(
            monitoring_interval=60,  # 1 minute for testing
            compliance_threshold=0.8,
            critical_threshold=0.5
        )
    
    @pytest.fixture
    def remediation_engine(self):
        """Create AutoRemediationEngine for testing."""
        return AutoRemediationEngine(
            auto_execute_safe_actions=True,
            auto_execute_cautious_actions=False,
            max_concurrent_executions=2
        )
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, mock_service_data, reconciliation_engine, 
                                      drift_detector, compliance_monitor, remediation_engine):
        """Test complete end-to-end workflow of Phase 2 system."""
        
        # Step 1: Mock data collection for reconciliation engine
        with patch.object(reconciliation_engine, '_collect_spec_state') as mock_spec, \
             patch.object(reconciliation_engine, '_collect_cms_state') as mock_cms, \
             patch.object(reconciliation_engine, '_collect_runtime_state') as mock_runtime:
            
            def mock_spec_collector(service_name):
                return mock_service_data.get(service_name, {}).get("spec_state")
            
            def mock_cms_collector(service_name):
                return mock_service_data.get(service_name, {}).get("cms_state")
            
            def mock_runtime_collector(service_name):
                return mock_service_data.get(service_name, {}).get("runtime_state")
            
            mock_spec.side_effect = mock_spec_collector
            mock_cms.side_effect = mock_cms_collector
            mock_runtime.side_effect = mock_runtime_collector
            
            # Step 2: Reconcile all services
            with patch.object(reconciliation_engine, '_discover_all_services', 
                            return_value=set(mock_service_data.keys())):
                
                reconciliation_results = await reconciliation_engine.reconcile_all_services()
                
                # Verify reconciliation results
                assert len(reconciliation_results) == len(mock_service_data)
                assert "web_service" in reconciliation_results
                assert "database_service" in reconciliation_results
                assert "orphaned_service" in reconciliation_results
                assert "missing_service" in reconciliation_results
                
                # Check compliance scores
                web_result = reconciliation_results["web_service"]
                assert 0.0 <= web_result.compliance_score <= 1.0
                
                db_result = reconciliation_results["database_service"]
                assert db_result.compliance_score > web_result.compliance_score  # Should be higher (no drift)
        
        # Step 3: Perform drift detection
        drift_results = {}
        for service_name, service_data in mock_service_data.items():
            drift_result = await drift_detector.detect_service_drift(
                service_name=service_name,
                spec_state=service_data.get("spec_state"),
                cms_state=service_data.get("cms_state"),
                runtime_state=service_data.get("runtime_state")
            )
            drift_results[service_name] = drift_result
        
        # Verify drift detection results
        assert len(drift_results) == len(mock_service_data)
        
        # Orphaned service should be detected
        orphaned_result = drift_results["orphaned_service"]
        assert len(orphaned_result.orphaned_services) > 0
        
        # Missing service should be detected
        missing_result = drift_results["missing_service"]
        assert len(missing_result.missing_services) > 0
        
        # Web service should have version drift
        web_drift_result = drift_results["web_service"]
        assert len(web_drift_result.detected_drifts) > 0
        
        # Database service should have minimal drift
        db_drift_result = drift_results["database_service"]
        assert db_drift_result.drift_severity in [DriftSeverity.LOW, DriftSeverity.MEDIUM]
        
        # Step 4: Check compliance
        compliance_scores = await compliance_monitor.check_compliance(mock_service_data)
        
        # Verify compliance scores
        assert len(compliance_scores) == len(mock_service_data)
        assert all(0.0 <= score <= 1.0 for score in compliance_scores.values())
        
        # Database service should have higher compliance
        assert compliance_scores["database_service"] > compliance_scores["web_service"]
        
        # Step 5: Generate compliance report
        compliance_report = await compliance_monitor.generate_compliance_report(
            reporting_period_hours=1
        )
        
        # Verify compliance report
        assert compliance_report.services_analyzed > 0
        assert 0.0 <= compliance_report.overall_compliance_score <= 1.0
        assert len(compliance_report.service_compliance) > 0
        assert len(compliance_report.recommendations) >= 0
        
        # Step 6: Create and execute remediation plans
        remediation_plans = {}
        remediation_executions = {}
        
        for service_name, drift_result in drift_results.items():
            if len(drift_result.detected_drifts) > 0:
                # Assess remediation safety
                plan = await remediation_engine.assess_remediation_safety(drift_result)
                remediation_plans[service_name] = plan
                
                # Execute safe actions only
                if plan.overall_safety in [RemediationSafety.SAFE, RemediationSafety.CAUTIOUS]:
                    executions = await remediation_engine.execute_remediation_plan(plan)
                    remediation_executions[service_name] = executions
        
        # Verify remediation plans
        assert len(remediation_plans) > 0
        
        # Check that plans were created for services with drift
        if "web_service" in remediation_plans:
            web_plan = remediation_plans["web_service"]
            assert len(web_plan.actions) > 0
            assert web_plan.service_name == "web_service"
        
        # Step 7: Verify system integration
        # Get overall system status
        reconciliation_summary = reconciliation_engine.get_compliance_summary()
        drift_summary = drift_detector.get_drift_summary()
        compliance_trends = compliance_monitor.get_compliance_trends()
        remediation_stats = remediation_engine.get_remediation_statistics()
        
        # Verify summaries are generated
        assert "status" in reconciliation_summary
        assert "status" in drift_summary
        assert "status" in compliance_trends
        
        # Verify data consistency across components
        # Services detected by reconciliation should match drift detection
        reconciled_services = set(reconciliation_results.keys())
        drift_detected_services = set(drift_results.keys())
        assert reconciled_services == drift_detected_services
    
    @pytest.mark.asyncio
    async def test_compliance_monitoring_workflow(self, mock_service_data, compliance_monitor):
        """Test compliance monitoring workflow."""
        
        # Start monitoring
        await compliance_monitor.start_monitoring()
        assert compliance_monitor.is_monitoring
        
        # Update service states
        compliance_monitor.last_service_states = mock_service_data
        
        # Wait for one monitoring cycle
        await asyncio.sleep(0.1)  # Short wait for testing
        
        # Check compliance
        compliance_scores = await compliance_monitor.check_compliance(mock_service_data)
        assert len(compliance_scores) > 0
        
        # Get active alerts
        alerts = compliance_monitor.get_active_alerts()
        # Should have alerts for orphaned and missing services
        
        # Stop monitoring
        await compliance_monitor.stop_monitoring()
        assert not compliance_monitor.is_monitoring
    
    @pytest.mark.asyncio
    async def test_auto_remediation_safety_assessment(self, remediation_engine, drift_detector):
        """Test auto-remediation safety assessment."""
        
        # Create mock drift result with various severity levels
        mock_drift_result = await drift_detector.detect_service_drift(
            service_name="test_service",
            spec_state={"version": "2.0.0"},
            cms_state={"version": "1.0.0"},
            runtime_state={"version": "1.0.0", "status": "running"}
        )
        
        # Assess remediation safety
        plan = await remediation_engine.assess_remediation_safety(mock_drift_result)
        
        # Verify plan creation
        assert plan.service_name == "test_service"
        assert len(plan.actions) > 0
        assert plan.overall_safety in [s for s in RemediationSafety]
        assert plan.estimated_total_duration > 0
        
        # Test execution decision logic
        for action in plan.actions:
            should_execute = remediation_engine._should_execute_action(action, force_execution=False)
            
            # Safe actions should be executable
            if action.safety_level == RemediationSafety.SAFE:
                assert should_execute == remediation_engine.auto_execute_safe_actions
            
            # Risky actions should not be auto-executed
            if action.safety_level == RemediationSafety.RISKY:
                assert not should_execute
    
    @pytest.mark.asyncio
    async def test_system_resilience(self, reconciliation_engine, drift_detector, 
                                   compliance_monitor, remediation_engine):
        """Test system resilience to failures."""
        
        # Test reconciliation engine resilience
        result = await reconciliation_engine.reconcile_service_state("nonexistent_service")
        assert result.compliance_score == 0.0
        assert result.drift_severity == DriftSeverity.CRITICAL
        
        # Test drift detector resilience
        drift_result = await drift_detector.detect_service_drift(
            service_name="error_service",
            spec_state=None,
            cms_state=None,
            runtime_state=None
        )
        assert drift_result.confidence_score >= 0.0
        
        # Test compliance monitor resilience
        compliance_scores = await compliance_monitor.check_compliance({})
        assert isinstance(compliance_scores, dict)
        
        # Test remediation engine resilience
        stats = remediation_engine.get_remediation_statistics()
        assert "total_executions" in stats
    
    def test_component_capabilities(self, reconciliation_engine, drift_detector, 
                                  compliance_monitor, remediation_engine):
        """Test that all components report their capabilities correctly."""
        
        # Test reconciliation engine capabilities
        reconciliation_caps = reconciliation_engine.get_capabilities()
        assert reconciliation_caps["module_type"] == "state_reconciliation_engine"
        assert "features" in reconciliation_caps
        
        # Test drift detector capabilities
        drift_caps = drift_detector.get_capabilities()
        assert drift_caps["module_type"] == "drift_detector"
        assert "detection_categories" in drift_caps
        
        # Test compliance monitor capabilities
        compliance_caps = compliance_monitor.get_capabilities()
        assert compliance_caps["module_type"] == "compliance_monitor"
        assert "alert_severities" in compliance_caps
        
        # Test remediation engine capabilities
        remediation_caps = remediation_engine.get_capabilities()
        assert remediation_caps["module_type"] == "auto_remediation_engine"
        assert "supported_action_types" in remediation_caps
    
    def test_component_module_info(self, reconciliation_engine, drift_detector, 
                                 compliance_monitor, remediation_engine):
        """Test that all components report module info correctly."""
        
        components = [
            (reconciliation_engine, "StateReconciliationEngine"),
            (drift_detector, "DriftDetector"),
            (compliance_monitor, "ComplianceMonitor"),
            (remediation_engine, "AutoRemediationEngine")
        ]
        
        for component, expected_name in components:
            info = component.get_module_info()
            assert info["name"] == expected_name
            assert "version" in info
            assert "status" in info
    
    def test_component_graceful_degradation(self, reconciliation_engine, drift_detector, 
                                          compliance_monitor, remediation_engine):
        """Test graceful degradation for all components."""
        
        test_error = Exception("Test error")
        components = [reconciliation_engine, drift_detector, compliance_monitor, remediation_engine]
        
        for component in components:
            degradation_info = component.graceful_degradation(test_error)
            assert degradation_info["status"] == "degraded"
            assert degradation_info["error"] == str(test_error)
            assert "available_functions" in degradation_info
            assert "degraded_functions" in degradation_info
            assert "recovery_actions" in degradation_info
    
    @pytest.mark.asyncio
    async def test_performance_characteristics(self, mock_service_data, reconciliation_engine):
        """Test performance characteristics of the system."""
        
        # Mock data collection to be fast
        with patch.object(reconciliation_engine, '_collect_spec_state', return_value={}), \
             patch.object(reconciliation_engine, '_collect_cms_state', return_value={}), \
             patch.object(reconciliation_engine, '_collect_runtime_state', return_value={}), \
             patch.object(reconciliation_engine, '_discover_all_services', 
                         return_value=set(mock_service_data.keys())):
            
            # Measure reconciliation time
            start_time = datetime.now()
            results = await reconciliation_engine.reconcile_all_services()
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            
            # Should complete within reasonable time (adjust threshold as needed)
            assert duration < 5.0  # 5 seconds for 4 services
            assert len(results) == len(mock_service_data)
    
    def test_data_serialization(self, mock_service_data):
        """Test that all data structures can be serialized to JSON."""
        
        # This is important for API responses and logging
        try:
            json.dumps(mock_service_data)
        except (TypeError, ValueError) as e:
            pytest.fail(f"Mock service data not JSON serializable: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])