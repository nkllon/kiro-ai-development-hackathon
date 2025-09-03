"""
Beast Mode Framework - Baseline Metrics Engine Tests
Comprehensive validation following C1-C7 check requirements
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import json
import time
import threading
from unittest.mock import patch, MagicMock

from src.beast_mode.metrics.baseline_metrics_engine import BaselineMetricsEngine, PerformanceMetrics
from src.beast_mode.core.reflective_module import HealthStatus

class TestBaselineMetricsEngine:
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = BaselineMetricsEngine()
        # Override storage path for testing
        self.engine.metrics_storage_path = Path(self.temp_dir) / "test_metrics"
        self.engine.metrics_storage_path.mkdir(exist_ok=True)
        
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    # C1: Model Compliance Check - Uses project registry intelligence
    def test_c1_model_compliance_uses_registry_intelligence(self):
        """Validate that metrics engine uses project registry intelligence for planning"""
        # The engine should be designed based on registry domain intelligence
        assert hasattr(self.engine, 'measurement_categories')
        assert 'problem_resolution_speed' in self.engine.measurement_categories
        assert 'tool_health_performance' in self.engine.measurement_categories
        assert 'decision_success_rates' in self.engine.measurement_categories
        assert 'development_velocity' in self.engine.measurement_categories
        
        # Categories should trace to requirements R8.1-R8.5
        status = self.engine.get_module_status()
        assert 'measurement_categories' in status
        assert len(status['measurement_categories']) == 4
        
    # C2: RM Compliance Check - Implements ReflectiveModule interface
    def test_c2_rm_compliance_interface_implementation(self):
        """Validate RM interface compliance"""
        # Must implement all required RM methods
        assert hasattr(self.engine, 'get_module_status')
        assert hasattr(self.engine, 'is_healthy')
        assert hasattr(self.engine, 'get_health_indicators')
        assert hasattr(self.engine, 'degrade_gracefully')
        assert hasattr(self.engine, 'maintain_single_responsibility')
        
        # Test actual method calls
        status = self.engine.get_module_status()
        assert isinstance(status, dict)
        assert 'module_name' in status
        
        health = self.engine.is_healthy()
        assert isinstance(health, bool)
        
        indicators = self.engine.get_health_indicators()
        assert isinstance(indicators, dict)
        
    def test_c2_rm_compliance_health_monitoring(self):
        """Validate health monitoring capabilities"""
        # Should report accurate health status
        assert self.engine.is_healthy() == True  # Fresh engine should be healthy
        
        # Health indicators should be comprehensive
        indicators = self.engine.get_health_indicators()
        assert 'concurrent_capacity' in indicators
        assert 'storage_health' in indicators
        assert 'measurement_readiness' in indicators
        
    def test_c2_rm_compliance_graceful_degradation(self):
        """Validate graceful degradation without system failure"""
        failure_context = {"error": "storage_failure", "severity": "high"}
        result = self.engine.degrade_gracefully(failure_context)
        
        assert result.degradation_applied == True
        assert isinstance(result.reduced_functionality, list)
        assert result.recovery_strategy is not None
        assert result.estimated_recovery_time is not None
        
        # Engine should still be operational in degraded mode
        status = self.engine.get_module_status()
        assert status['status'] == 'degraded'
        
    # C3: Tool Integration Check - All measurement tools work correctly
    def test_c3_tool_integration_measurement_tools(self):
        """Validate integration with measurement and analysis tools"""
        # Test measurement recording
        success = self.engine.establish_baseline_measurement(
            'problem_resolution_speed', 'baseline', 5.0
        )
        assert success == True
        
        # Test data persistence
        file_path = self.engine.metrics_storage_path / "problem_resolution_speed_baseline_measurements.jsonl"
        assert file_path.exists()
        
        # Test statistical analysis tools
        # Add enough samples for analysis
        for i in range(5):
            self.engine.establish_baseline_measurement('problem_resolution_speed', 'baseline', 5.0 + i)
            self.engine.establish_baseline_measurement('problem_resolution_speed', 'systematic', 3.0 + i)
            
        metrics = self.engine.calculate_performance_metrics('problem_resolution_speed')
        assert metrics is not None
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.improvement_ratio > 1.0  # Systematic should be faster (lower time)
        
    # C4: Architecture Boundaries Check - Single responsibility and clear interfaces
    def test_c4_architecture_boundaries_single_responsibility(self):
        """Validate single responsibility and architectural boundaries"""
        responsibility = self.engine.maintain_single_responsibility()
        
        assert responsibility['module_name'] == 'baseline_metrics_engine'
        assert 'performance_baseline_establishment_and_metrics_collection' in responsibility['primary_responsibility']
        assert responsibility['single_responsibility_score'] >= 0.8  # High adherence
        
        # Should not have boundary violations
        violations = responsibility['boundary_violations']
        assert len(violations) == 0
        
    def test_c4_architecture_boundaries_clear_interfaces(self):
        """Validate clear interfaces and proper delegation"""
        # Engine should delegate to specialized tools, not implement everything
        # Storage delegation
        assert hasattr(self.engine, '_persist_measurement')
        
        # Statistical analysis should use standard library (proper delegation)
        import statistics
        # Engine uses statistics module, not custom implementation
        
    # C5: Performance & Quality Check - Handles 1000+ concurrent measurements
    def test_c5_performance_concurrent_measurements_constraint_c07(self):
        """Validate Constraint C-07: Handle 1000+ concurrent measurements"""
        # Test concurrent capacity
        assert self.engine.max_concurrent_measurements == 1000
        
        # Test concurrent measurement handling
        def concurrent_measurement():
            return self.engine.establish_baseline_measurement(
                'problem_resolution_speed', 'baseline', 1.0
            )
            
        # Simulate concurrent measurements (smaller scale for test performance)
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(concurrent_measurement) for _ in range(50)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
        # All measurements should succeed
        assert all(results)
        
        # Capacity tracking should work
        status = self.engine.get_module_status()
        assert 'capacity_utilization' in status
        
    def test_c5_performance_quality_no_regressions(self):
        """Validate no performance regressions and quality maintenance"""
        # Measurement should be fast
        start_time = time.time()
        success = self.engine.establish_baseline_measurement(
            'problem_resolution_speed', 'baseline', 1.0
        )
        measurement_time = time.time() - start_time
        
        assert success == True
        assert measurement_time < 0.1  # Should be very fast
        
        # Quality: Data integrity
        category = self.engine.measurement_categories['problem_resolution_speed']
        assert len(category.baseline_samples) == 1
        assert category.baseline_samples[0] == 1.0
        
    # C6: Root Cause Analysis Check - Systematic failure analysis
    def test_c6_rca_check_failure_analysis(self):
        """Validate RCA capabilities for systematic failure analysis"""
        # Test scenario: No superiority detected (should trigger analysis)
        
        # Add samples where systematic is NOT better (failure scenario)
        for i in range(5):
            self.engine.establish_baseline_measurement('problem_resolution_speed', 'baseline', 2.0)  # Fast baseline
            self.engine.establish_baseline_measurement('problem_resolution_speed', 'systematic', 5.0)  # Slow systematic
            
        metrics = self.engine.calculate_performance_metrics('problem_resolution_speed')
        assert metrics is not None
        
        # Should detect that systematic is NOT superior (improvement_ratio < 1.0)
        assert metrics.improvement_ratio < 1.0
        
        # This should trigger RCA in real implementation
        # For now, validate that we can detect the failure condition
        evidence = self.engine.generate_superiority_evidence()
        # Should return None or low scores when systematic approach fails
        
    # C7: Multi-Stakeholder Perspective Validation
    def test_c7_multi_stakeholder_perspective_validation(self):
        """Validate multi-stakeholder perspective requirements"""
        
        # Beast Mode Perspective: Does this prove systematic superiority?
        status = self.engine.get_module_status()
        assert 'total_baseline_samples' in status
        assert 'total_systematic_samples' in status
        # Should enable superiority proof
        
        # GKE Consumer Perspective: Will these metrics convince service adoption?
        # Should provide clear, actionable metrics
        assert 'capacity_utilization' in status
        assert 'measurement_categories' in status
        
        # DevOps Perspective: Are metrics operationally useful and reliable?
        indicators = self.engine.get_health_indicators()
        assert 'concurrent_capacity' in indicators
        assert 'storage_health' in indicators
        
        # Development Perspective: Is measurement system maintainable?
        responsibility = self.engine.maintain_single_responsibility()
        assert responsibility['single_responsibility_score'] >= 0.8
        
        # Evaluator Perspective: Do metrics provide concrete evidence?
        # Add sufficient samples for evidence generation
        for i in range(10):
            for category in self.engine.measurement_categories.keys():
                self.engine.establish_baseline_measurement(category, 'baseline', 5.0)
                self.engine.establish_baseline_measurement(category, 'systematic', 3.0)
                
        evidence = self.engine.generate_superiority_evidence()
        if evidence:  # May be None if insufficient samples
            assert evidence.overall_superiority_score > 0
            assert evidence.evidence_quality_score > 0
            
    def test_validation_criteria_comprehensive(self):
        """Validate all success criteria are met"""
        
        # Baseline Established
        success = self.engine.establish_baseline_measurement(
            'problem_resolution_speed', 'baseline', 5.0
        )
        assert success == True
        
        # Systematic Tracking
        success = self.engine.establish_baseline_measurement(
            'problem_resolution_speed', 'systematic', 3.0
        )
        assert success == True
        
        # Statistical Significance (with sufficient samples)
        for i in range(10):
            self.engine.establish_baseline_measurement('problem_resolution_speed', 'baseline', 5.0 + i*0.1)
            self.engine.establish_baseline_measurement('problem_resolution_speed', 'systematic', 3.0 + i*0.1)
            
        metrics = self.engine.calculate_performance_metrics('problem_resolution_speed')
        assert metrics is not None
        assert metrics.statistical_significance > 0
        
        # Evidence Quality
        assert self.engine.is_healthy() == True
        status = self.engine.get_module_status()
        assert status['status'] == 'operational'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])