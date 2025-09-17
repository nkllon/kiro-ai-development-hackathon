"""
Rca Integration Services Validation

This module was extracted from rca_integration_services.py
as part of RM-DDD compliance refactoring.
"""

import re
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..analysis.rca_engine import RCAEngine, Failure, FailureCategory, RCAResult, RootCauseType, PreventionPattern
from .performance_monitor import RCAPerformanceMonitor, ResourceLimits, PerformanceStatus
from .timeout_handler import RCATimeoutHandler, TimeoutConfiguration, TimeoutStrategy
from .test_pattern_library import TestPatternLibrary
from .error_handler import RCAErrorHandler, DegradationLevel
from src.rm_ddd.core.health import ModuleHealth


def analyze_test_failures(self, failures: List[TestFailureData]) -> TestRCAReportData:
    """
        Comprehensive analysis workflow for test failures with performance monitoring and timeout handling
        Requirements: 1.1, 1.2, 2.1, 1.4, 4.2 - Automatic RCA analysis with 30-second timeout and performance optimization
        """
    operation_id = f'test_rca_analysis_{int(time.time())}_{len(failures)}_failures'
    self.total_test_failures_processed += len(failures)
    try:
        self.logger.info(f'Starting RCA analysis for {len(failures)} test failures with comprehensive error handling')
        with self.error_handler.handle_rca_operation('analyze_test_failures', 'test_rca_integrator'):
            with self.performance_monitor.monitor_operation(operation_id, timeout_seconds=30) as perf_metrics:
                with self.timeout_handler.manage_operation_timeout(operation_id, self._handle_degradation_callback) as timeout_context:
                    grouped_failures = self.group_related_failures(failures)
                    self.logger.info(f'Grouped {len(failures)} failures into {len(grouped_failures)} groups')
                    prioritized_failures = self.prioritize_failures(failures)
                    rca_failures = []
                    for test_failure in prioritized_failures:
                        rca_failure = self.convert_to_rca_failure(test_failure)
                        rca_failures.append(rca_failure)
                    rca_results = []
                    pattern_matches = []
                    degradation_applied = False
                    for i, rca_failure in enumerate(rca_failures):
                        try:
                            elapsed_time = (datetime.now() - perf_metrics.start_time).total_seconds()
                            timeout_recommendations = self.timeout_handler.get_timeout_recommendations(operation_id, elapsed_time)
                            if timeout_recommendations.get('degradation_suggested', False) and (not degradation_applied):
                                self.logger.warning(f'Applying graceful degradation based on timeout recommendations')
                                degradation_result = self.timeout_handler.apply_graceful_degradation(operation_id, degradation_level=1)
                                degradation_applied = True
                                if degradation_result.get('success', False):
                                    existing_patterns = self.rca_engine.match_existing_patterns(rca_failure)
                                    pattern_matches.extend(existing_patterns)
                                    self.pattern_matches_found += len(existing_patterns)
                                    continue
                            if i % 5 == 0:
                                self.performance_monitor.optimize_resource_usage(operation_id)
                            existing_patterns = self.rca_engine.match_existing_patterns(rca_failure)
                            test_specific_patterns = self.test_pattern_library.match_test_patterns(rca_failure)
                            all_patterns = existing_patterns + test_specific_patterns
                            pattern_matches.extend(all_patterns)
                            self.pattern_matches_found += len(all_patterns)
                            if not degradation_applied:
                                try:
                                    rca_result = self.rca_engine.perform_systematic_rca(rca_failure)
                                    rca_results.append(rca_result)
                                    self.successful_rca_analyses += 1
                                except Exception as rca_error:
                                    self.logger.warning(f'RCA engine failed for {rca_failure.failure_id}, using error handler')
                                    fallback_result = self.error_handler.handle_rca_engine_failure(failure=rca_failure, error=rca_error, rca_engine=self.rca_engine)
                                    if hasattr(fallback_result, 'failure_id'):
                                        rca_results.append(fallback_result)
                                    else:
                                        self.logger.info(f'Generated fallback report for {rca_failure.failure_id}')
                                        continue
                                if rca_result.rca_confidence_score > 0.8 and rca_result.validation_results and any((v.fix_successful for v in rca_result.validation_results)):
                                    avg_validation_score = sum((v.confidence_score for v in rca_result.validation_results)) / len(rca_result.validation_results)
                                    learning_success = self.test_pattern_library.learn_from_successful_rca(failure=rca_failure, root_causes=rca_result.root_causes, systematic_fixes=rca_result.systematic_fixes, validation_score=avg_validation_score)
                                    if learning_success:
                                        self.logger.info(f'Learned new test pattern from successful RCA: {rca_failure.failure_id}')
                            if elapsed_time > 25:
                                self.logger.warning(f'Approaching timeout limit: {elapsed_time:.2f}s')
                                if not degradation_applied:
                                    self.timeout_handler.apply_graceful_degradation(operation_id, degradation_level=2)
                                    degradation_applied = True
                                    break
                        except Exception as e:
                            self.logger.error(f'RCA analysis failed for failure {rca_failure.failure_id}: {e}')
                            continue
                    report = self.generate_comprehensive_report(failures, grouped_failures, rca_results, pattern_matches)
                    if hasattr(report, 'performance_metrics'):
                        report.performance_metrics = {'analysis_duration_seconds': perf_metrics.duration_seconds, 'memory_usage_mb': perf_metrics.memory_usage_mb, 'peak_memory_mb': perf_metrics.peak_memory_mb, 'timeout_occurred': perf_metrics.timeout_occurred, 'graceful_degradation': perf_metrics.graceful_degradation, 'performance_status': perf_metrics.operation_status.value}
                    self.total_analysis_time += perf_metrics.duration_seconds
                    self.logger.info(f'RCA analysis complete: {len(rca_results)} analyses in {perf_metrics.duration_seconds:.2f}s')
                    return report
    except Exception as e:
        self.logger.error(f'Test RCA analysis failed: {e}')
        return self.error_handler.generate_fallback_report(failures, e)

def get_test_pattern_effectiveness_report(self) -> Dict[str, Any]:
    """
        Get test pattern library effectiveness report
        Requirements: 2.4, 4.2, 4.4 - Pattern effectiveness and performance monitoring
        """
    try:
        pattern_report = self.test_pattern_library.get_pattern_effectiveness_report()
        integration_metrics = {'pattern_integration_success_rate': self.pattern_matches_found / max(1, self.successful_rca_analyses), 'patterns_learned_from_rca': len([r for r in self.test_pattern_library.learning_data if r.successful_fix_applied]), 'average_pattern_match_time_ms': pattern_report.get('average_match_time_ms', 0.0), 'sub_second_performance_met': pattern_report.get('average_match_time_ms', 0.0) < 1000}
        pattern_report['integration_metrics'] = integration_metrics
        return pattern_report
    except Exception as e:
        self.logger.error(f'Failed to generate test pattern effectiveness report: {e}')
        return {'error': str(e), 'timestamp': datetime.now().isoformat()}

def optimize_test_pattern_library(self) -> Dict[str, Any]:
    """
        Optimize test pattern library performance and cleanup
        Requirements: 4.2 - Performance optimization and maintenance
        """
    try:
        optimization_results = {'pattern_optimization': {}, 'library_cleanup': {}, 'performance_improvement': 0.0}
        current_report = self.test_pattern_library.get_pattern_effectiveness_report()
        baseline_match_time = current_report.get('average_match_time_ms', 0.0)
        pattern_optimization = self.test_pattern_library.optimize_pattern_performance()
        optimization_results['pattern_optimization'] = pattern_optimization
        cleanup_results = self.test_pattern_library.cleanup_pattern_library()
        optimization_results['library_cleanup'] = cleanup_results
        new_report = self.test_pattern_library.get_pattern_effectiveness_report()
        new_match_time = new_report.get('average_match_time_ms', 0.0)
        optimization_results['performance_improvement'] = baseline_match_time - new_match_time
        self.logger.info(f"Test pattern library optimization complete: removed {cleanup_results.get('duplicate_patterns_removed', 0)} duplicates, performance improvement: {optimization_results['performance_improvement']:.2f}ms")
        return optimization_results
    except Exception as e:
        self.logger.error(f'Test pattern library optimization failed: {e}')
        return {'error': str(e), 'timestamp': datetime.now().isoformat()}

def _categorize_test_failure(self, test_failure: TestFailureData) -> FailureCategory:
    """Categorize test failure for RCA analysis"""
    error_msg = test_failure.error_message.lower()
    if 'importerror' in error_msg or 'modulenotfounderror' in error_msg:
        return FailureCategory.DEPENDENCY_ISSUE
    elif 'permissionerror' in error_msg or 'permission denied' in error_msg:
        return FailureCategory.PERMISSION_ISSUE
    elif 'filenotfounderror' in error_msg or 'no such file' in error_msg:
        return FailureCategory.CONFIGURATION_ERROR
    elif 'connectionerror' in error_msg or 'network' in error_msg:
        return FailureCategory.NETWORK_CONNECTIVITY
    elif 'memoryerror' in error_msg or 'resource' in error_msg:
        return FailureCategory.RESOURCE_EXHAUSTION
    elif test_failure.failure_type in ['timeout', 'hanging']:
        return FailureCategory.RESOURCE_EXHAUSTION
    else:
        return FailureCategory.UNKNOWN

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

