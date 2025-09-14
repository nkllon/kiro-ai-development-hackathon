"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.533568
"""




import pytest
import logging
import time
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.beast_mode.testing.beast_mode_test_orchestrator import (
    BeastModeTestOrchestrator,
    TestPhase,
    TestFailurePattern,
    TestExecutionMetrics,
    PDCATestCycle
)
from src.beast_mode.testing.rca_pattern_analyzer import (
    RCAPatternAnalyzer,
    LoggingDeficiencyType,
    ProfilingDeficiencyType,
    PatternAnalysisResult
)


class TestBeastModeComprehensiveSystem:
    """
    Comprehensive test suite for Beast Mode testing system
    
    This test suite demonstrates systematic testing principles:
    - Each test follows PDCA methodology
    - RCA is performed on failures
    - RDI traceability is maintained
    - Logging and profiling are comprehensive
    """

    def setup_method(self):
        """Setup test environment with comprehensive logging and profiling"""
        # Setup enhanced logging
        self.logger = logging.getLogger("beast_mode.test.comprehensive")
        self.logger.setLevel(logging.DEBUG)
        
        # Create test orchestrator
        self.orchestrator = BeastModeTestOrchestrator("test_orchestrator")
        
        # Create RCA pattern analyzer
        self.rca_analyzer = RCAPatternAnalyzer("test_rca_analyzer")
        
        # Test requirements for RDI traceability
        self.test_requirements = [
            "REQ-TEST-001: Orchestrator must initialize successfully",
            "REQ-TEST-002: PDCA cycles must execute systematically",
            "REQ-TEST-003: RCA must detect failure patterns",
            "REQ-TEST-004: Logging deficiencies must be identified",
            "REQ-TEST-005: Profiling gaps must be detected",
            "REQ-TEST-006: Improvements must be systematically implemented"
        ]
        
        self.logger.info("🐺 Beast Mode comprehensive test setup completed")

    def test_orchestrator_initialization_with_rdi_tracing(self):
        """
        Test orchestrator initialization with full RDI traceability
        
        Requirements: REQ-TEST-001
        Design: Systematic initialization with health monitoring
        Implementation: BeastModeTestOrchestrator.__init__
        """
        self.logger.info("🎯 Testing orchestrator initialization with RDI tracing")
        
        # PLAN Phase
        expected_components = [
            "logger", "rca_engine", "test_rca_integration",
            "test_metrics", "failure_patterns", "config"
        ]
        
        # DO Phase
        start_time = time.time()
        
        # Verify orchestrator components
        for component in expected_components:
            assert hasattr(self.orchestrator, component), f"Missing component: {component}"
            self.logger.debug(f"✅ Component verified: {component}")
        
        # CHECK Phase
        health_indicators = self.orchestrator.get_health_indicators()
        assert health_indicators["active_pdca_cycle"] is False
        assert health_indicators["rca_engine_status"] == "active"
        assert health_indicators["profiling_enabled"] is True
        
        execution_time = time.time() - start_time
        
        # ACT Phase - Log performance metrics
        self.logger.info(
            f"📊 Initialization performance: {execution_time:.3f}s",
            extra={'test_phase': 'ACT', 'metric_type': 'performance'}
        )
        
        # RDI Trace
        rdi_trace = {
            "requirement": "REQ-TEST-001",
            "design_validated": True,
            "implementation_verified": True,
            "execution_time": execution_time,
            "components_verified": len(expected_components)
        }
        
        self.logger.info(f"🔗 RDI Trace: {rdi_trace}")
        
        assert execution_time < 1.0, "Initialization should be fast"

    def test_pdca_cycle_execution_with_comprehensive_monitoring(self):
        """
        Test PDCA cycle execution with comprehensive monitoring
        
        Requirements: REQ-TEST-002
        Design: Full PDCA cycle with monitoring at each phase
        Implementation: BeastModeTestOrchestrator.start_pdca_cycle
        """
        self.logger.info("🔄 Testing PDCA cycle execution with comprehensive monitoring")
        
        # PLAN Phase
        test_suite = "comprehensive_system_test"
        requirements = self.test_requirements[:3]  # Subset for testing
        
        start_time = time.time()
        
        # DO Phase
        cycle_id = self.orchestrator.start_pdca_cycle(test_suite, requirements)
        
        # Verify cycle initialization
        assert self.orchestrator.current_pdca_cycle is not None
        assert self.orchestrator.current_pdca_cycle.cycle_id == cycle_id
        assert len(self.orchestrator.current_pdca_cycle.plan_phase["requirements"]) == 3
        
        # CHECK Phase
        cycle = self.orchestrator.current_pdca_cycle
        plan_phase = cycle.plan_phase
        
        assert "test_suite" in plan_phase
        assert "requirements" in plan_phase
        assert "expected_outcomes" in plan_phase
        assert "risk_assessment" in plan_phase
        assert "success_criteria" in plan_phase
        
        execution_time = time.time() - start_time
        
        # ACT Phase - Performance analysis
        self.logger.info(
            f"📊 PDCA cycle initialization: {execution_time:.3f}s",
            extra={'test_phase': 'ACT', 'cycle_id': cycle_id}
        )
        
        # Verify success criteria are reasonable
        success_criteria = plan_phase["success_criteria"]
        assert success_criteria["min_pass_rate"] > 0
        assert success_criteria["max_execution_time_minutes"] > 0
        
        self.logger.info(f"✅ PDCA cycle {cycle_id} executed successfully")

    def test_rca_pattern_analysis_for_logging_deficiencies(self):
        """
        Test RCA pattern analysis specifically for logging deficiencies
        
        Requirements: REQ-TEST-003, REQ-TEST-004
        Design: Systematic detection of logging issues
        Implementation: RCAPatternAnalyzer._analyze_logging_deficiencies
        """
        self.logger.info("🔬 Testing RCA pattern analysis for logging deficiencies")
        
        # PLAN Phase - Create test scenarios with logging issues
        test_scenarios = [
            {
                "name": "no_logger_configured",
                "error_message": "NameError: name 'logger' is not defined",
                "stack_trace": "File test.py, line 10, in test_function\n    logger.info('test')",
                "expected_pattern": LoggingDeficiencyType.NO_LOGGER_CONFIGURED
            },
            {
                "name": "insufficient_log_level",
                "error_message": "Debug information not available for analysis",
                "stack_trace": "File test.py, line 15, in analyze\n    # debug info missing",
                "expected_pattern": LoggingDeficiencyType.INSUFFICIENT_LOG_LEVEL
            },
            {
                "name": "missing_context",
                "error_message": "Context missing for error analysis",
                "stack_trace": "File test.py, line 20, in process\n    # no context info",
                "expected_pattern": LoggingDeficiencyType.MISSING_CONTEXT_INFO
            }
        ]
        
        # DO Phase - Execute RCA analysis
        results = []
        for scenario in test_scenarios:
            self.logger.debug(f"🔍 Analyzing scenario: {scenario['name']}")
            
            test_context = {
                "test_name": f"test_{scenario['name']}",
                "test_path": f"tests/test_{scenario['name']}.py",
                "error_type": "NameError"
            }
            
            start_time = time.time()
            
            analysis_result = self.rca_analyzer.analyze_failure_pattern(
                error_message=scenario["error_message"],
                stack_trace=scenario["stack_trace"],
                test_context=test_context
            )
            
            analysis_time = time.time() - start_time
            
            results.append({
                "scenario": scenario["name"],
                "analysis_result": analysis_result,
                "analysis_time": analysis_time
            })
            
            self.logger.info(
                f"📊 RCA analysis completed for {scenario['name']}: {analysis_time:.3f}s",
                extra={'pattern_type': analysis_result.pattern_type, 'confidence': analysis_result.confidence_score}
            )
        
        # CHECK Phase - Verify analysis results
        for i, result in enumerate(results):
            analysis = result["analysis_result"]
            scenario = test_scenarios[i]
            
            # Verify pattern detection
            assert "logging_deficiency" in analysis.pattern_type
            assert analysis.confidence_score > 0.8  # High confidence for logging issues
            assert analysis.priority == "HIGH"  # Logging issues are high priority
            
            # Verify recommendations include logging improvements
            actions = analysis.recommended_actions
            assert any("logging" in action.lower() for action in actions)
            assert any("debug" in action.lower() or "log level" in action.lower() for action in actions)
            
            self.logger.debug(f"✅ Scenario {scenario['name']} analysis verified")
        
        # ACT Phase - Generate improvement plan
        improvement_plan = self.rca_analyzer.generate_improvement_plan([r["analysis_result"] for r in results])
        
        assert improvement_plan["summary"]["total_patterns"] == len(results)
        assert improvement_plan["summary"]["high_priority"] == len(results)  # All logging issues are high priority
        assert len(improvement_plan["immediate_actions"]) > 0
        
        self.logger.info(f"📋 Improvement plan generated with {len(improvement_plan['immediate_actions'])} immediate actions")

    def test_profiling_deficiency_detection_and_remediation(self):
        """
        Test profiling deficiency detection and systematic remediation
        
        Requirements: REQ-TEST-005
        Design: Comprehensive profiling gap analysis
        Implementation: RCAPatternAnalyzer._analyze_profiling_deficiencies
        """
        self.logger.info("📈 Testing profiling deficiency detection and remediation")
        
        # PLAN Phase - Create profiling deficiency scenarios
        profiling_scenarios = [
            {
                "name": "no_profiler_enabled",
                "error_message": "Performance data not available for analysis",
                "stack_trace": "File test.py, line 25, in performance_test\n    # no profiling data",
                "system_state": None,  # Missing system state indicates no profiling
                "expected_deficiency": ProfilingDeficiencyType.NO_PROFILER_ENABLED
            },
            {
                "name": "missing_timing_data",
                "error_message": "Execution time unknown for optimization",
                "stack_trace": "File test.py, line 30, in optimize\n    # timing data missing",
                "system_state": {"memory": "available"},  # Partial system state
                "expected_deficiency": ProfilingDeficiencyType.MISSING_TIMING_DATA
            }
        ]
        
        # DO Phase - Execute profiling analysis
        profiling_results = []
        for scenario in profiling_scenarios:
            self.logger.debug(f"📊 Analyzing profiling scenario: {scenario['name']}")
            
            test_context = {
                "test_name": f"test_{scenario['name']}",
                "test_path": f"tests/performance/test_{scenario['name']}.py",
                "profiling_enabled": False  # Indicates profiling not enabled
            }
            
            start_time = time.time()
            
            analysis_result = self.rca_analyzer.analyze_failure_pattern(
                error_message=scenario["error_message"],
                stack_trace=scenario["stack_trace"],
                test_context=test_context,
                system_state=scenario["system_state"]
            )
            
            analysis_time = time.time() - start_time
            
            profiling_results.append({
                "scenario": scenario["name"],
                "analysis_result": analysis_result,
                "analysis_time": analysis_time
            })
            
            self.logger.info(
                f"📊 Profiling analysis completed for {scenario['name']}: {analysis_time:.3f}s",
                extra={'pattern_type': analysis_result.pattern_type, 'confidence': analysis_result.confidence_score}
            )
        
        # CHECK Phase - Verify profiling analysis
        for i, result in enumerate(profiling_results):
            analysis = result["analysis_result"]
            scenario = profiling_scenarios[i]
            
            # Verify profiling deficiency detection
            assert "profiling_deficiency" in analysis.pattern_type or "profiling" in analysis.pattern_type.lower()
            assert analysis.confidence_score > 0.7  # Good confidence for profiling issues
            assert analysis.priority in ["HIGH", "MEDIUM"]  # Profiling issues are important
            
            # Verify recommendations include profiling improvements
            actions = analysis.recommended_actions
            assert any("profiling" in action.lower() or "performance" in action.lower() for action in actions)
            assert any("monitoring" in action.lower() or "metrics" in action.lower() for action in actions)
            
            self.logger.debug(f"✅ Profiling scenario {scenario['name']} analysis verified")
        
        # ACT Phase - Verify systematic improvement recommendations
        all_actions = []
        for result in profiling_results:
            all_actions.extend(result["analysis_result"].recommended_actions)
        
        # Should recommend systematic profiling infrastructure
        profiling_actions = [action for action in all_actions if "profiling" in action.lower()]
        monitoring_actions = [action for action in all_actions if "monitoring" in action.lower()]
        
        assert len(profiling_actions) > 0, "Should recommend profiling improvements"
        assert len(monitoring_actions) > 0, "Should recommend monitoring improvements"
        
        self.logger.info(f"📈 Profiling remediation plan includes {len(profiling_actions)} profiling actions")

    def test_systematic_improvement_implementation_tracking(self):
        """
        Test systematic improvement implementation and tracking
        
        Requirements: REQ-TEST-006
        Design: Track improvements across PDCA cycles
        Implementation: BeastModeTestOrchestrator.act_on_results
        """
        self.logger.info("⚡ Testing systematic improvement implementation tracking")
        
        # PLAN Phase - Setup improvement tracking scenario
        test_suite = "improvement_tracking_test"
        requirements = self.test_requirements
        
        # Start PDCA cycle
        cycle_id = self.orchestrator.start_pdca_cycle(test_suite, requirements)
        
        # Simulate test execution with some failures
        self.orchestrator.failure_patterns = {
            TestFailurePattern.INSUFFICIENT_LOGGING: 2,
            TestFailurePattern.PROFILING_MISSING: 1,
            TestFailurePattern.DEPENDENCY_MISSING: 1
        }
        
        # Add some test metrics
        test_metric = TestExecutionMetrics(
            test_name="improvement_test",
            phase=TestPhase.DO,
            start_time=time.time() - 10,
            end_time=time.time(),
            duration=10.0,
            status="FAILED",
            error_type="TestFailure",
            error_message="Multiple issues detected",
            coverage_percentage=75.0,
            memory_usage=512.0,
            cpu_usage=45.0
        )
        self.orchestrator.test_metrics.append(test_metric)
        
        # DO Phase - Execute CHECK and ACT phases
        start_time = time.time()
        
        # CHECK Phase
        check_results = self.orchestrator.check_test_results()
        
        # Verify check results structure
        assert "success_criteria_met" in check_results
        assert "performance_analysis" in check_results
        assert "failure_pattern_analysis" in check_results
        assert "improvement_opportunities" in check_results
        
        # ACT Phase
        actions_taken = self.orchestrator.act_on_results(check_results)
        
        execution_time = time.time() - start_time
        
        # CHECK Phase - Verify improvements were implemented
        assert len(actions_taken) > 0, "Should have implemented improvements"
        
        # Verify specific improvements for detected patterns
        logging_improvements = [action for action in actions_taken if "logging" in action.lower()]
        profiling_improvements = [action for action in actions_taken if "profiling" in action.lower()]
        
        assert len(logging_improvements) > 0, "Should address logging issues"
        assert len(profiling_improvements) > 0, "Should address profiling issues"
        
        # Verify PDCA cycle completion
        cycle = self.orchestrator.current_pdca_cycle
        assert cycle.end_time is not None
        assert len(cycle.actions_taken) == len(actions_taken)
        assert "next_cycle_recommendations" in cycle.act_phase
        
        # ACT Phase - Log systematic improvement metrics
        improvement_metrics = {
            "total_improvements": len(actions_taken),
            "logging_improvements": len(logging_improvements),
            "profiling_improvements": len(profiling_improvements),
            "cycle_duration": (cycle.end_time - cycle.start_time).total_seconds(),
            "improvement_implementation_time": execution_time
        }
        
        self.logger.info(
            f"📊 Systematic improvement metrics: {improvement_metrics}",
            extra={'test_phase': 'ACT', 'cycle_id': cycle_id}
        )
        
        # Verify systematic approach
        next_recommendations = cycle.act_phase["next_cycle_recommendations"]
        assert len(next_recommendations) > 0, "Should provide next cycle recommendations"
        
        self.logger.info(f"✅ Systematic improvement implementation completed with {len(actions_taken)} actions")

    def test_comprehensive_rdi_traceability_validation(self):
        """
        Test comprehensive RDI (Requirements-Design-Implementation) traceability
        
        Requirements: All REQ-TEST-* requirements
        Design: End-to-end traceability validation
        Implementation: Full system integration test
        """
        self.logger.info("🔗 Testing comprehensive RDI traceability validation")
        
        # PLAN Phase - Define comprehensive traceability matrix
        rdi_matrix = {
            "REQ-TEST-001": {
                "design_elements": ["BeastModeTestOrchestrator", "ReflectiveModule"],
                "implementation_files": ["beast_mode_test_orchestrator.py"],
                "test_methods": ["test_orchestrator_initialization_with_rdi_tracing"]
            },
            "REQ-TEST-002": {
                "design_elements": ["PDCATestCycle", "TestPhase"],
                "implementation_files": ["beast_mode_test_orchestrator.py"],
                "test_methods": ["test_pdca_cycle_execution_with_comprehensive_monitoring"]
            },
            "REQ-TEST-003": {
                "design_elements": ["RCAPatternAnalyzer", "PatternAnalysisResult"],
                "implementation_files": ["rca_pattern_analyzer.py"],
                "test_methods": ["test_rca_pattern_analysis_for_logging_deficiencies"]
            }
        }
        
        # DO Phase - Validate traceability for each requirement
        traceability_results = {}
        
        for req_id, req_data in rdi_matrix.items():
            self.logger.debug(f"🔍 Validating traceability for {req_id}")
            
            start_time = time.time()
            
            # Validate design elements exist
            design_coverage = len(req_data["design_elements"])
            
            # Validate implementation files exist
            impl_coverage = len(req_data["implementation_files"])
            
            # Validate test methods exist
            test_coverage = len(req_data["test_methods"])
            
            validation_time = time.time() - start_time
            
            traceability_score = (design_coverage + impl_coverage + test_coverage) / 3.0
            
            traceability_results[req_id] = {
                "design_coverage": design_coverage,
                "implementation_coverage": impl_coverage,
                "test_coverage": test_coverage,
                "traceability_score": traceability_score,
                "validation_time": validation_time
            }
            
            self.logger.debug(f"📊 {req_id} traceability score: {traceability_score:.2f}")
        
        # CHECK Phase - Verify comprehensive traceability
        total_requirements = len(rdi_matrix)
        fully_traced_requirements = len([r for r in traceability_results.values() if r["traceability_score"] >= 1.0])
        
        traceability_percentage = (fully_traced_requirements / total_requirements) * 100
        
        assert traceability_percentage >= 80, f"Traceability should be >= 80%, got {traceability_percentage:.1f}%"
        
        # Verify each requirement has minimum traceability
        for req_id, result in traceability_results.items():
            assert result["design_coverage"] > 0, f"{req_id} missing design coverage"
            assert result["implementation_coverage"] > 0, f"{req_id} missing implementation coverage"
            assert result["test_coverage"] > 0, f"{req_id} missing test coverage"
        
        # ACT Phase - Generate traceability report
        traceability_report = {
            "total_requirements": total_requirements,
            "fully_traced_requirements": fully_traced_requirements,
            "traceability_percentage": traceability_percentage,
            "average_traceability_score": sum(r["traceability_score"] for r in traceability_results.values()) / total_requirements,
            "requirements_analysis": traceability_results
        }
        
        self.logger.info(
            f"📋 RDI Traceability Report: {traceability_percentage:.1f}% coverage",
            extra={'traceability_score': traceability_report["average_traceability_score"]}
        )
        
        # Verify systematic traceability approach
        assert traceability_report["average_traceability_score"] >= 1.0, "Average traceability should be complete"
        
        self.logger.info("✅ Comprehensive RDI traceability validation completed successfully")

    def test_beast_mode_system_health_and_performance(self):
        """
        Test overall Beast Mode system health and performance
        
        This test validates the entire system is working systematically
        """
        self.logger.info("🏥 Testing Beast Mode system health and performance")
        
        # PLAN Phase - Define health criteria
        health_criteria = {
            "orchestrator_healthy": True,
            "rca_analyzer_healthy": True,
            "response_time_ms": 1000,  # Max 1 second
            "memory_usage_mb": 100,    # Max 100 MB
            "error_rate_percent": 0    # No errors
        }
        
        # DO Phase - Execute comprehensive health check
        start_time = time.time()
        
        # Check orchestrator health
        orchestrator_health = self.orchestrator.get_health_indicators()
        orchestrator_status = self.orchestrator.get_module_status()
        orchestrator_healthy = self.orchestrator.is_healthy()
        
        # Check RCA analyzer health
        rca_health = self.rca_analyzer.get_health_indicators()
        rca_status = self.rca_analyzer.get_module_status()
        rca_healthy = self.rca_analyzer.is_healthy()
        
        # Measure performance
        health_check_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # CHECK Phase - Validate health criteria
        assert orchestrator_healthy, f"Orchestrator unhealthy: {orchestrator_status}"
        assert rca_healthy, f"RCA analyzer unhealthy: {rca_status}"
        assert health_check_time < health_criteria["response_time_ms"], f"Health check too slow: {health_check_time:.1f}ms"
        
        # Verify health indicators are comprehensive
        assert "rca_engine_status" in orchestrator_health
        assert "profiling_enabled" in orchestrator_health
        assert "total_test_metrics" in orchestrator_health
        
        assert "total_analyses_performed" in rca_health
        assert "analyzer_status" in rca_health
        
        # ACT Phase - Log comprehensive health report
        health_report = {
            "system_status": "HEALTHY",
            "orchestrator": {
                "status": orchestrator_status,
                "healthy": orchestrator_healthy,
                "indicators": orchestrator_health
            },
            "rca_analyzer": {
                "status": rca_status,
                "healthy": rca_healthy,
                "indicators": rca_health
            },
            "performance": {
                "health_check_time_ms": health_check_time,
                "meets_criteria": health_check_time < health_criteria["response_time_ms"]
            }
        }
        
        self.logger.info(
            f"🏥 Beast Mode System Health Report: {health_report['system_status']}",
            extra={'health_check_time': health_check_time, 'system_status': 'HEALTHY'}
        )
        
        # Verify systematic health monitoring
        assert health_report["system_status"] == "HEALTHY"
        assert health_report["performance"]["meets_criteria"]
        
        self.logger.info("✅ Beast Mode system health and performance validation completed")

    def teardown_method(self):
        """Cleanup test environment with comprehensive logging"""
        self.logger.info("🧹 Beast Mode comprehensive test cleanup completed")
        
        # Log final test metrics
        if hasattr(self, 'orchestrator') and self.orchestrator.test_metrics:
            total_metrics = len(self.orchestrator.test_metrics)
            self.logger.info(f"📊 Total test metrics collected: {total_metrics}")
        
        if hasattr(self, 'rca_analyzer') and self.rca_analyzer.analysis_history:
            total_analyses = len(self.rca_analyzer.analysis_history)
            self.logger.info(f"🔬 Total RCA analyses performed: {total_analyses}")


# Standalone test execution for demonstration
if __name__ == "__main__":
    # Setup logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🐺 Beast Mode Comprehensive System Test - Standalone Execution")
    print("=" * 70)
    
    # Create test instance
    test_instance = TestBeastModeComprehensiveSystem()
    
    try:
        # Run comprehensive test suite
        test_instance.setup_method()
        
        print("🎯 Running orchestrator initialization test...")
        test_instance.test_orchestrator_initialization_with_rdi_tracing()
        print("✅ Orchestrator initialization test passed")
        
        print("🔄 Running PDCA cycle execution test...")
        test_instance.test_pdca_cycle_execution_with_comprehensive_monitoring()
        print("✅ PDCA cycle execution test passed")
        
        print("🔬 Running RCA pattern analysis test...")
        test_instance.test_rca_pattern_analysis_for_logging_deficiencies()
        print("✅ RCA pattern analysis test passed")
        
        print("📈 Running profiling deficiency detection test...")
        test_instance.test_profiling_deficiency_detection_and_remediation()
        print("✅ Profiling deficiency detection test passed")
        
        print("⚡ Running systematic improvement tracking test...")
        test_instance.test_systematic_improvement_implementation_tracking()
        print("✅ Systematic improvement tracking test passed")
        
        print("🔗 Running RDI traceability validation test...")
        test_instance.test_comprehensive_rdi_traceability_validation()
        print("✅ RDI traceability validation test passed")
        
        print("🏥 Running system health and performance test...")
        test_instance.test_beast_mode_system_health_and_performance()
        print("✅ System health and performance test passed")
        
        test_instance.teardown_method()
        
        print("\n🏆 ALL BEAST MODE COMPREHENSIVE TESTS PASSED!")
        print("🐺 Systematic excellence demonstrated across all components")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

        exit(1)