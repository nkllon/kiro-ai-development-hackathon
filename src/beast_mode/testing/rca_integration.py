"""
Beast Mode Framework - Test RCA Integration Layer
Implements integration between test failures and RCA engine for systematic analysis
Requirements: 1.1, 1.2, 2.1, 4.1, 4.3
"""

import re
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..analysis.rca_engine import (
    RCAEngine, Failure, FailureCategory, RCAResult, 
    RootCauseType, PreventionPattern
)
from .performance_monitor import RCAPerformanceMonitor, ResourceLimits, PerformanceStatus
from .timeout_handler import RCATimeoutHandler, TimeoutConfiguration, TimeoutStrategy


@dataclass
class TestFailureData:
    """Test failure data model from design document"""
    test_name: str
    test_file: str
    failure_type: str  # assertion, error, timeout, etc.
    error_message: str
    stack_trace: str
    test_function: str
    test_class: Optional[str]
    failure_timestamp: datetime
    test_context: Dict[str, Any]
    pytest_node_id: str


@dataclass
class TestRCASummaryData:
    """Summary of test RCA analysis results"""
    most_common_root_causes: List[Tuple[RootCauseType, int]]
    systematic_fixes_available: int
    pattern_matches_found: int
    estimated_fix_time_minutes: int
    confidence_score: float
    critical_issues: List[str]


@dataclass
class TestRCAReportData:
    """Complete test RCA analysis report"""
    analysis_timestamp: datetime
    total_failures: int
    failures_analyzed: int
    grouped_failures: Dict[str, List[TestFailureData]]
    rca_results: List[RCAResult]
    summary: TestRCASummaryData
    recommendations: List[str]
    prevention_patterns: List[PreventionPattern]
    next_steps: List[str]


class TestFailurePriorityLevel(Enum):
    """Priority levels for test failure analysis"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestRCAIntegrationEngine(ReflectiveModule):
    """
    Integration layer between test failures and RCA engine
    Provides failure grouping, prioritization, and comprehensive analysis workflow
    """
    
    def __init__(self, rca_engine: Optional[RCAEngine] = None, 
                 performance_monitor: Optional[RCAPerformanceMonitor] = None,
                 timeout_handler: Optional[RCATimeoutHandler] = None):
        super().__init__("test_rca_integrator")
        
        # Initialize RCA engine
        self.rca_engine = rca_engine or RCAEngine()
        
        # Initialize performance monitoring and timeout handling
        # Requirements: 1.4, 4.2 - Performance optimization and timeout handling
        self.performance_monitor = performance_monitor or RCAPerformanceMonitor(
            ResourceLimits(
                max_memory_mb=512,
                max_cpu_percent=80.0,
                timeout_seconds=30,
                warning_threshold_seconds=25,
                memory_warning_threshold_mb=400
            )
        )
        
        self.timeout_handler = timeout_handler or RCATimeoutHandler(
            TimeoutConfiguration(
                primary_timeout_seconds=30,
                warning_timeout_seconds=25,
                graceful_timeout_seconds=20,
                hard_timeout_seconds=35,
                strategy=TimeoutStrategy.GRACEFUL_DEGRADATION,
                enable_progressive_degradation=True,
                max_degradation_levels=3
            )
        )
        
        # Start performance monitoring
        self.performance_monitor.start_monitoring()
        
        # Integration metrics
        self.total_test_failures_processed = 0
        self.successful_rca_analyses = 0
        self.pattern_matches_found = 0
        self.total_analysis_time = 0.0
        
        # Failure grouping configuration
        self.max_failures_per_group = 10
        self.analysis_timeout_seconds = 30
        
        self._update_health_indicator(
            "test_rca_integration_readiness",
            HealthStatus.HEALTHY,
            "ready",
            "Test RCA integration layer ready for failure analysis"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for external systems"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "test_failures_processed": self.total_test_failures_processed,
            "successful_rca_analyses": self.successful_rca_analyses,
            "pattern_matches_found": self.pattern_matches_found,
            "average_analysis_time": self.total_analysis_time / max(1, self.successful_rca_analyses),
            "rca_engine_status": self.rca_engine.get_module_status() if self.rca_engine else "unavailable",
            "performance_monitor_status": self.performance_monitor.get_module_status(),
            "timeout_handler_status": self.timeout_handler.get_module_status(),
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for test RCA integration capability"""
        return (not self._degradation_active and 
                self.rca_engine is not None and 
                self.rca_engine.is_healthy() and
                self.performance_monitor.is_healthy() and
                self.timeout_handler.is_healthy())
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for operational visibility"""
        return {
            "integration_capability": {
                "status": "healthy" if not self._degradation_active else "degraded",
                "failures_processed": self.total_test_failures_processed,
                "success_rate": self.successful_rca_analyses / max(1, self.total_test_failures_processed)
            },
            "rca_engine_integration": {
                "status": "healthy" if self.rca_engine and self.rca_engine.is_healthy() else "degraded",
                "engine_available": self.rca_engine is not None,
                "pattern_match_rate": self.pattern_matches_found / max(1, self.successful_rca_analyses)
            },
            "performance": {
                "status": "healthy" if self.total_analysis_time / max(1, self.successful_rca_analyses) < 30 else "degraded",
                "average_analysis_time": self.total_analysis_time / max(1, self.successful_rca_analyses),
                "timeout_compliance": "within_30_seconds"
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: Test failure to RCA integration"""
        return "test_failure_rca_integration_and_analysis"
        
    def analyze_test_failures(self, failures: List[TestFailureData]) -> TestRCAReportData:
        """
        Comprehensive analysis workflow for test failures with performance monitoring and timeout handling
        Requirements: 1.1, 1.2, 2.1, 1.4, 4.2 - Automatic RCA analysis with 30-second timeout and performance optimization
        """
        operation_id = f"test_rca_analysis_{int(time.time())}_{len(failures)}_failures"
        self.total_test_failures_processed += len(failures)
        
        try:
            self.logger.info(f"Starting RCA analysis for {len(failures)} test failures with performance monitoring")
            
            # Use performance monitoring and timeout handling
            with self.performance_monitor.monitor_operation(operation_id, timeout_seconds=30) as perf_metrics:
                with self.timeout_handler.manage_operation_timeout(operation_id, self._handle_degradation_callback) as timeout_context:
                    
                    # Step 1: Group related failures for efficient analysis
                    grouped_failures = self.group_related_failures(failures)
                    self.logger.info(f"Grouped {len(failures)} failures into {len(grouped_failures)} groups")
                    
                    # Step 2: Prioritize failures for analysis order
                    prioritized_failures = self.prioritize_failures(failures)
                    
                    # Step 3: Convert test failures to RCA-compatible Failure objects
                    rca_failures = []
                    for test_failure in prioritized_failures:
                        rca_failure = self.convert_to_rca_failure(test_failure)
                        rca_failures.append(rca_failure)
                        
                    # Step 4: Perform RCA analysis on each failure with timeout monitoring
                    rca_results = []
                    pattern_matches = []
                    degradation_applied = False
                    
                    for i, rca_failure in enumerate(rca_failures):
                        try:
                            # Check timeout recommendations before each analysis
                            elapsed_time = (datetime.now() - perf_metrics.start_time).total_seconds()
                            timeout_recommendations = self.timeout_handler.get_timeout_recommendations(operation_id, elapsed_time)
                            
                            # Apply graceful degradation if recommended
                            if timeout_recommendations.get("degradation_suggested", False) and not degradation_applied:
                                self.logger.warning(f"Applying graceful degradation based on timeout recommendations")
                                degradation_result = self.timeout_handler.apply_graceful_degradation(operation_id, degradation_level=1)
                                degradation_applied = True
                                
                                if degradation_result.get("success", False):
                                    # Switch to fast pattern matching only
                                    existing_patterns = self.rca_engine.match_existing_patterns(rca_failure)
                                    pattern_matches.extend(existing_patterns)
                                    self.pattern_matches_found += len(existing_patterns)
                                    continue
                            
                            # Optimize resource usage periodically
                            if i % 5 == 0:  # Every 5 failures
                                self.performance_monitor.optimize_resource_usage(operation_id)
                            
                            # Check for existing patterns first (fast path)
                            existing_patterns = self.rca_engine.match_existing_patterns(rca_failure)
                            pattern_matches.extend(existing_patterns)
                            self.pattern_matches_found += len(existing_patterns)
                            
                            # Perform comprehensive RCA analysis if not degraded
                            if not degradation_applied:
                                rca_result = self.rca_engine.perform_systematic_rca(rca_failure)
                                rca_results.append(rca_result)
                                self.successful_rca_analyses += 1
                            
                            # Check if we're approaching timeout limits
                            if elapsed_time > 25:  # 25 seconds warning threshold
                                self.logger.warning(f"Approaching timeout limit: {elapsed_time:.2f}s")
                                if not degradation_applied:
                                    # Apply emergency degradation
                                    self.timeout_handler.apply_graceful_degradation(operation_id, degradation_level=2)
                                    degradation_applied = True
                                    break
                                    
                        except Exception as e:
                            self.logger.error(f"RCA analysis failed for failure {rca_failure.failure_id}: {e}")
                            continue
                            
                    # Step 5: Generate comprehensive report
                    report = self.generate_comprehensive_report(
                        failures, grouped_failures, rca_results, pattern_matches
                    )
                    
                    # Add performance metrics to report
                    if hasattr(report, 'performance_metrics'):
                        report.performance_metrics = {
                            "analysis_duration_seconds": perf_metrics.duration_seconds,
                            "memory_usage_mb": perf_metrics.memory_usage_mb,
                            "peak_memory_mb": perf_metrics.peak_memory_mb,
                            "timeout_occurred": perf_metrics.timeout_occurred,
                            "graceful_degradation": perf_metrics.graceful_degradation,
                            "performance_status": perf_metrics.operation_status.value
                        }
                    
                    self.total_analysis_time += perf_metrics.duration_seconds
                    self.logger.info(f"RCA analysis complete: {len(rca_results)} analyses in {perf_metrics.duration_seconds:.2f}s")
                    return report
            
        except Exception as e:
            self.logger.error(f"Test RCA analysis failed: {e}")
            # Return minimal report on failure
            return TestRCAReportData(
                analysis_timestamp=datetime.now(),
                total_failures=len(failures),
                failures_analyzed=0,
                grouped_failures={},
                rca_results=[],
                summary=TestRCASummaryData([], 0, 0, 0, 0.0, [f"Analysis failed: {e}"]),
                recommendations=[f"RCA analysis failed: {e}"],
                prevention_patterns=[],
                next_steps=["Check RCA engine health", "Retry analysis with simplified parameters"]
            )
            
    def group_related_failures(self, failures: List[TestFailureData]) -> Dict[str, List[TestFailureData]]:
        """
        Group related test failures for efficient batch analysis
        Requirements: 1.3, 5.1, 5.2, 5.3, 5.4 - Advanced failure grouping with correlation detection
        """
        grouped_failures = {}
        
        try:
            # Step 1: Initial grouping by basic characteristics
            basic_groups = self._create_basic_failure_groups(failures)
            
            # Step 2: Advanced correlation detection within groups
            correlated_groups = self._detect_failure_correlations(basic_groups)
            
            # Step 3: Merge highly correlated groups
            final_groups = self._merge_correlated_groups(correlated_groups)
            
            # Step 4: Apply size limits and create overflow groups
            grouped_failures = self._apply_group_size_limits(final_groups)
            
            self.logger.info(f"Advanced grouping complete: {[(k, len(v)) for k, v in grouped_failures.items()]}")
            return grouped_failures
            
        except Exception as e:
            self.logger.error(f"Advanced failure grouping failed: {e}")
            # Fallback: each failure in its own group
            return {f"failure_{i}": [failure] for i, failure in enumerate(failures)}
            
    def prioritize_failures(self, failures: List[TestFailureData]) -> List[TestFailureData]:
        """
        Advanced prioritization system for analyzing most critical failures first
        Requirements: 1.3, 5.1, 5.2, 5.3, 5.4 - Multi-dimensional failure prioritization
        """
        try:
            # Step 1: Calculate multi-dimensional priority scores
            scored_failures = []
            for failure in failures:
                base_score = self._calculate_failure_priority_score(failure)
                impact_score = self._calculate_failure_impact_score(failure)
                urgency_score = self._calculate_failure_urgency_score(failure)
                correlation_score = self._calculate_correlation_priority_score(failure, failures)
                
                total_score = (base_score * 0.4 + impact_score * 0.3 + 
                              urgency_score * 0.2 + correlation_score * 0.1)
                
                scored_failures.append((failure, total_score))
            
            # Step 2: Sort by total score (highest first)
            prioritized = [failure for failure, score in sorted(scored_failures, key=lambda x: x[1], reverse=True)]
            
            # Step 3: Apply priority boosting for critical patterns
            prioritized = self._apply_critical_priority_boosting(prioritized)
            
            priority_info = [(f.test_name, self._get_failure_priority(f).value, 
                            scored_failures[i][1]) for i, f in enumerate(prioritized[:5])]
            self.logger.info(f"Top 5 prioritized failures: {priority_info}")
            
            return prioritized
            
        except Exception as e:
            self.logger.error(f"Advanced failure prioritization failed: {e}")
            return failures  # Return original order on failure
            
    def convert_to_rca_failure(self, test_failure: TestFailureData) -> Failure:
        """
        Convert TestFailure object to RCA-compatible Failure object
        Requirements: 4.1 - Integration with existing RCAEngine
        """
        try:
            # Generate unique failure ID
            failure_id = f"test_{hashlib.md5(test_failure.pytest_node_id.encode()).hexdigest()[:8]}"
            
            # Determine failure category based on test failure type
            category = self._categorize_test_failure(test_failure)
            
            # Create comprehensive context for RCA analysis
            context = {
                "test_file": test_failure.test_file,
                "test_function": test_failure.test_function,
                "test_class": test_failure.test_class,
                "pytest_node_id": test_failure.pytest_node_id,
                "failure_type": test_failure.failure_type,
                "test_context": test_failure.test_context,
                "analysis_source": "test_rca_integrator"
            }
            
            return Failure(
                failure_id=failure_id,
                timestamp=test_failure.failure_timestamp,
                component=f"test:{test_failure.test_file}",
                error_message=test_failure.error_message,
                stack_trace=test_failure.stack_trace,
                context=context,
                category=category
            )
            
        except Exception as e:
            self.logger.error(f"Failed to convert test failure to RCA failure: {e}")
            # Return minimal failure object
            return Failure(
                failure_id=f"test_conversion_failed_{int(time.time())}",
                timestamp=datetime.now(),
                component="test:unknown",
                error_message=f"Conversion failed: {e}",
                stack_trace=None,
                context={"conversion_error": str(e)},
                category=FailureCategory.UNKNOWN
            )
            
    def generate_comprehensive_report(
        self, 
        original_failures: List[TestFailureData],
        grouped_failures: Dict[str, List[TestFailureData]],
        rca_results: List[RCAResult],
        pattern_matches: List[PreventionPattern]
    ) -> TestRCAReportData:
        """
        Generate comprehensive RCA report for test failures
        Requirements: 2.2, 2.3, 2.4 - Detailed reporting with actionable recommendations
        """
        try:
            # Generate summary statistics
            summary = self._generate_rca_summary(rca_results, pattern_matches)
            
            # Generate actionable recommendations
            recommendations = self._generate_recommendations(rca_results)
            
            # Extract prevention patterns
            all_prevention_patterns = []
            for result in rca_results:
                all_prevention_patterns.extend(result.prevention_patterns)
            all_prevention_patterns.extend(pattern_matches)
            
            # Generate next steps
            next_steps = self._generate_next_steps(rca_results, summary)
            
            return TestRCAReportData(
                analysis_timestamp=datetime.now(),
                total_failures=len(original_failures),
                failures_analyzed=len(rca_results),
                grouped_failures=grouped_failures,
                rca_results=rca_results,
                summary=summary,
                recommendations=recommendations,
                prevention_patterns=all_prevention_patterns,
                next_steps=next_steps
            )
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return TestRCAReportData(
                analysis_timestamp=datetime.now(),
                total_failures=len(original_failures),
                failures_analyzed=0,
                grouped_failures=grouped_failures,
                rca_results=rca_results,
                summary=TestRCASummaryData([], 0, 0, 0, 0.0, [f"Report generation failed: {e}"]),
                recommendations=[f"Report generation failed: {e}"],
                prevention_patterns=[],
                next_steps=["Check report generation system", "Retry with simplified parameters"]
            )
            
    def analyze_batch_failures(self, failure_groups: Dict[str, List[TestFailureData]]) -> Dict[str, List[RCAResult]]:
        """
        Batch RCA analysis for processing multiple failures efficiently
        Requirements: 5.1, 5.2, 5.3, 5.4 - Efficient batch processing with correlation analysis
        """
        batch_results = {}
        
        try:
            for group_name, group_failures in failure_groups.items():
                self.logger.info(f"Processing batch group '{group_name}' with {len(group_failures)} failures")
                
                # Convert to RCA failures
                rca_failures = [self.convert_to_rca_failure(f) for f in group_failures]
                
                # Detect common patterns within the group
                common_patterns = self._detect_common_failure_patterns(group_failures)
                
                # Perform batch analysis with shared context
                group_results = []
                shared_context = self._build_shared_analysis_context(group_failures, common_patterns)
                
                for rca_failure in rca_failures:
                    # Enhance failure context with shared information
                    rca_failure.context.update(shared_context)
                    
                    # Perform RCA with batch optimizations
                    result = self.rca_engine.perform_systematic_rca(rca_failure)
                    group_results.append(result)
                    
                batch_results[group_name] = group_results
                
            return batch_results
            
        except Exception as e:
            self.logger.error(f"Batch failure analysis failed: {e}")
            return {}

    def detect_failure_correlations(self, failures: List[TestFailureData]) -> Dict[str, Any]:
        """
        Detect correlations and common root causes across multiple failures
        Requirements: 5.1, 5.2, 5.3, 5.4 - Failure correlation detection
        """
        correlations = {
            "temporal_correlations": [],
            "error_pattern_correlations": [],
            "dependency_correlations": [],
            "environmental_correlations": [],
            "common_root_causes": []
        }
        
        try:
            # Temporal correlation analysis
            correlations["temporal_correlations"] = self._analyze_temporal_correlations(failures)
            
            # Error pattern correlation analysis
            correlations["error_pattern_correlations"] = self._analyze_error_pattern_correlations(failures)
            
            # Dependency correlation analysis
            correlations["dependency_correlations"] = self._analyze_dependency_correlations(failures)
            
            # Environmental correlation analysis
            correlations["environmental_correlations"] = self._analyze_environmental_correlations(failures)
            
            # Common root cause identification
            correlations["common_root_causes"] = self._identify_common_root_causes(failures)
            
            self.logger.info(f"Correlation analysis complete: {len(correlations['common_root_causes'])} common root causes found")
            return correlations
            
        except Exception as e:
            self.logger.error(f"Failure correlation detection failed: {e}")
            return correlations

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive performance report for RCA operations
        Requirements: 4.2 - Performance monitoring and metrics collection
        """
        try:
            performance_report = self.performance_monitor.get_performance_report()
            timeout_status = self.timeout_handler.get_module_status()
            
            return {
                "rca_integration_performance": {
                    "total_operations": performance_report.total_operations,
                    "successful_operations": performance_report.successful_operations,
                    "timeout_operations": performance_report.timeout_operations,
                    "degraded_operations": performance_report.degraded_operations,
                    "average_duration_seconds": performance_report.average_duration_seconds,
                    "average_memory_usage_mb": performance_report.average_memory_usage_mb,
                    "peak_memory_usage_mb": performance_report.peak_memory_usage_mb,
                    "timeout_rate": performance_report.timeout_rate,
                    "degradation_rate": performance_report.degradation_rate,
                    "performance_trend": performance_report.performance_trend
                },
                "timeout_management": {
                    "timeout_compliance_rate": 1.0 - timeout_status.get("hard_timeout_rate", 0.0),
                    "graceful_degradation_success_rate": timeout_status.get("successful_degradation_rate", 0.0),
                    "primary_timeout_seconds": timeout_status.get("primary_timeout_seconds", 30),
                    "timeout_strategy": timeout_status.get("timeout_strategy", "graceful_degradation")
                },
                "integration_metrics": {
                    "test_failures_processed": self.total_test_failures_processed,
                    "successful_rca_analyses": self.successful_rca_analyses,
                    "pattern_matches_found": self.pattern_matches_found,
                    "rca_success_rate": self.successful_rca_analyses / max(1, self.total_test_failures_processed),
                    "pattern_match_rate": self.pattern_matches_found / max(1, self.successful_rca_analyses)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
    def optimize_performance_configuration(self) -> Dict[str, Any]:
        """
        Optimize performance configuration based on historical data
        Requirements: 4.2 - Performance optimization
        """
        try:
            optimization_result = {
                "optimization_applied": False,
                "optimizations": [],
                "performance_improvement_expected": 0.0
            }
            
            # Optimize timeout configuration
            timeout_optimization = self.timeout_handler.optimize_timeout_configuration()
            if timeout_optimization.get("optimization_applied", False):
                optimization_result["optimizations"].append(timeout_optimization)
                optimization_result["optimization_applied"] = True
                optimization_result["performance_improvement_expected"] += timeout_optimization.get("performance_improvement_expected", 0.0)
            
            # Optimize resource limits based on usage patterns
            performance_report = self.performance_monitor.get_performance_report()
            if performance_report.average_memory_usage_mb > 0:
                current_limit = self.performance_monitor.resource_limits.max_memory_mb
                optimal_limit = int(performance_report.peak_memory_usage_mb * 1.2)  # 20% buffer
                
                if optimal_limit != current_limit and optimal_limit > 256:  # Minimum 256MB
                    self.performance_monitor.resource_limits.max_memory_mb = optimal_limit
                    optimization_result["optimizations"].append({
                        "type": "memory_limit_optimization",
                        "previous_limit_mb": current_limit,
                        "new_limit_mb": optimal_limit,
                        "reason": "adjusted_based_on_peak_usage"
                    })
                    optimization_result["optimization_applied"] = True
            
            # Optimize failure grouping based on performance
            if performance_report.average_duration_seconds > 20:  # If taking too long
                if self.max_failures_per_group > 5:
                    self.max_failures_per_group = max(5, self.max_failures_per_group - 2)
                    optimization_result["optimizations"].append({
                        "type": "failure_grouping_optimization",
                        "new_max_failures_per_group": self.max_failures_per_group,
                        "reason": "reduce_analysis_time"
                    })
                    optimization_result["optimization_applied"] = True
            
            self.logger.info(f"Performance optimization result: {optimization_result}")
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"Performance optimization failed: {e}")
            return {
                "optimization_applied": False,
                "error": str(e)
            }
            
    def _handle_degradation_callback(self, degradation_config: Dict[str, Any]) -> None:
        """
        Handle graceful degradation callback from timeout handler
        Requirements: 1.4 - Graceful degradation implementation
        """
        try:
            self.logger.info(f"Applying degradation configuration: {degradation_config}")
            
            # Store degradation configuration for use in analysis
            self._current_degradation_config = degradation_config
            
            # Adjust analysis parameters based on degradation level
            if degradation_config.get("analysis_scope") == "reduced":
                # Reduce the number of failures analyzed per group
                self.max_failures_per_group = min(5, self.max_failures_per_group)
                
            elif degradation_config.get("analysis_scope") == "pattern_matching_only":
                # Skip comprehensive analysis, use pattern matching only
                self._pattern_matching_only = True
                
            elif degradation_config.get("analysis_scope") == "minimal":
                # Minimal analysis - basic error reporting only
                self._minimal_analysis_mode = True
                
            self.logger.info("Degradation configuration applied successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to apply degradation configuration: {e}")

    # Private helper methods for advanced grouping and analysis
    
    def _create_basic_failure_groups(self, failures: List[TestFailureData]) -> Dict[str, List[TestFailureData]]:
        """Create initial failure groups based on basic characteristics"""
        basic_groups = {}
        
        for failure in failures:
            group_key = self._generate_failure_group_key(failure)
            
            if group_key not in basic_groups:
                basic_groups[group_key] = []
            basic_groups[group_key].append(failure)
            
        return basic_groups
    
    def _detect_failure_correlations(self, basic_groups: Dict[str, List[TestFailureData]]) -> Dict[str, List[TestFailureData]]:
        """Detect correlations within and across basic groups"""
        correlated_groups = {}
        
        for group_name, group_failures in basic_groups.items():
            if len(group_failures) <= 1:
                correlated_groups[group_name] = group_failures
                continue
                
            # Analyze correlations within the group
            correlation_matrix = self._build_correlation_matrix(group_failures)
            
            # Split highly correlated failures into subgroups
            subgroups = self._split_by_correlation(group_failures, correlation_matrix)
            
            for i, subgroup in enumerate(subgroups):
                subgroup_name = f"{group_name}_corr_{i}" if len(subgroups) > 1 else group_name
                correlated_groups[subgroup_name] = subgroup
                
        return correlated_groups
    
    def _merge_correlated_groups(self, correlated_groups: Dict[str, List[TestFailureData]]) -> Dict[str, List[TestFailureData]]:
        """Merge groups that show high correlation across group boundaries"""
        merged_groups = {}
        processed_groups = set()
        
        group_names = list(correlated_groups.keys())
        
        for i, group_a in enumerate(group_names):
            if group_a in processed_groups:
                continue
                
            merged_group = correlated_groups[group_a][:]
            merged_name = group_a
            processed_groups.add(group_a)
            
            # Check for mergeable groups
            for j, group_b in enumerate(group_names[i+1:], i+1):
                if group_b in processed_groups:
                    continue
                    
                # Calculate cross-group correlation
                correlation_score = self._calculate_cross_group_correlation(
                    correlated_groups[group_a], correlated_groups[group_b]
                )
                
                # Merge if highly correlated
                if correlation_score > 0.7:
                    merged_group.extend(correlated_groups[group_b])
                    merged_name = f"{merged_name}_merged_{group_b}"
                    processed_groups.add(group_b)
                    
            merged_groups[merged_name] = merged_group
            
        return merged_groups
    
    def _apply_group_size_limits(self, groups: Dict[str, List[TestFailureData]]) -> Dict[str, List[TestFailureData]]:
        """Apply size limits and create overflow groups"""
        limited_groups = {}
        
        for group_name, group_failures in groups.items():
            if len(group_failures) <= self.max_failures_per_group:
                limited_groups[group_name] = group_failures
            else:
                # Split large groups
                for i in range(0, len(group_failures), self.max_failures_per_group):
                    chunk = group_failures[i:i + self.max_failures_per_group]
                    chunk_name = f"{group_name}_chunk_{i // self.max_failures_per_group}"
                    limited_groups[chunk_name] = chunk
                    
        return limited_groups
    
    def _calculate_failure_impact_score(self, failure: TestFailureData) -> float:
        """Calculate impact score based on failure characteristics"""
        impact_score = 0.0
        
        # Infrastructure failures have high impact
        if any(keyword in failure.test_file.lower() for keyword in 
               ['conftest', 'fixture', 'setup', '__init__']):
            impact_score += 50.0
            
        # Import failures block other tests
        if failure.failure_type == 'import':
            impact_score += 40.0
            
        # Configuration failures affect multiple tests
        if any(keyword in failure.error_message.lower() for keyword in 
               ['config', 'environment', 'setting']):
            impact_score += 30.0
            
        # Security-related failures are high impact
        if any(keyword in failure.error_message.lower() for keyword in 
               ['security', 'permission', 'access', 'auth']):
            impact_score += 35.0
            
        return impact_score
    
    def _calculate_failure_urgency_score(self, failure: TestFailureData) -> float:
        """Calculate urgency score based on timing and context"""
        urgency_score = 0.0
        
        # Recent failures are more urgent
        time_since_failure = (datetime.now() - failure.failure_timestamp).total_seconds()
        if time_since_failure < 300:  # 5 minutes
            urgency_score += 30.0
        elif time_since_failure < 1800:  # 30 minutes
            urgency_score += 20.0
        elif time_since_failure < 3600:  # 1 hour
            urgency_score += 10.0
            
        # CI/CD context increases urgency
        if failure.test_context.get('environment_variables', {}).get('CI'):
            urgency_score += 25.0
            
        return urgency_score
    
    def _calculate_correlation_priority_score(self, failure: TestFailureData, all_failures: List[TestFailureData]) -> float:
        """Calculate priority score based on correlation with other failures"""
        correlation_score = 0.0
        
        # Count similar failures
        similar_failures = 0
        for other_failure in all_failures:
            if other_failure != failure:
                similarity = self._calculate_failure_similarity(failure, other_failure)
                if similarity > 0.5:
                    similar_failures += 1
                    
        # More correlated failures get higher priority
        correlation_score = min(similar_failures * 10.0, 50.0)
        
        return correlation_score
    
    def _apply_critical_priority_boosting(self, prioritized_failures: List[TestFailureData]) -> List[TestFailureData]:
        """Apply priority boosting for critical failure patterns"""
        critical_patterns = [
            'system', 'critical', 'fatal', 'security', 'corruption'
        ]
        
        critical_failures = []
        normal_failures = []
        
        for failure in prioritized_failures:
            is_critical = any(pattern in failure.error_message.lower() 
                            for pattern in critical_patterns)
            
            if is_critical:
                critical_failures.append(failure)
            else:
                normal_failures.append(failure)
                
        # Critical failures go first
        return critical_failures + normal_failures
    
    def _build_correlation_matrix(self, failures: List[TestFailureData]) -> List[List[float]]:
        """Build correlation matrix for failures within a group"""
        n = len(failures)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 1.0
                else:
                    matrix[i][j] = self._calculate_failure_similarity(failures[i], failures[j])
                    
        return matrix
    
    def _split_by_correlation(self, failures: List[TestFailureData], correlation_matrix: List[List[float]]) -> List[List[TestFailureData]]:
        """Split failures into subgroups based on correlation matrix"""
        n = len(failures)
        if n <= 1:
            return [failures]
            
        # Simple clustering based on correlation threshold
        threshold = 0.6
        groups = []
        assigned = [False] * n
        
        for i in range(n):
            if assigned[i]:
                continue
                
            group = [failures[i]]
            assigned[i] = True
            
            for j in range(i + 1, n):
                if not assigned[j] and correlation_matrix[i][j] > threshold:
                    group.append(failures[j])
                    assigned[j] = True
                    
            groups.append(group)
            
        return groups
    
    def _calculate_cross_group_correlation(self, group_a: List[TestFailureData], group_b: List[TestFailureData]) -> float:
        """Calculate correlation score between two groups"""
        if not group_a or not group_b:
            return 0.0
            
        total_similarity = 0.0
        comparisons = 0
        
        for failure_a in group_a:
            for failure_b in group_b:
                total_similarity += self._calculate_failure_similarity(failure_a, failure_b)
                comparisons += 1
                
        return total_similarity / comparisons if comparisons > 0 else 0.0
    
    def _calculate_failure_similarity(self, failure_a: TestFailureData, failure_b: TestFailureData) -> float:
        """Calculate similarity score between two failures"""
        similarity = 0.0
        
        # Same test file
        if failure_a.test_file == failure_b.test_file:
            similarity += 0.3
            
        # Same failure type
        if failure_a.failure_type == failure_b.failure_type:
            similarity += 0.2
            
        # Similar error messages
        error_similarity = self._calculate_text_similarity(failure_a.error_message, failure_b.error_message)
        similarity += error_similarity * 0.3
        
        # Similar stack traces
        if failure_a.stack_trace and failure_b.stack_trace:
            trace_similarity = self._calculate_text_similarity(failure_a.stack_trace, failure_b.stack_trace)
            similarity += trace_similarity * 0.2
            
        return min(similarity, 1.0)
    
    def _calculate_text_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate similarity between two text strings"""
        if not text_a or not text_b:
            return 0.0
            
        # Simple word-based similarity
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        
        if not words_a or not words_b:
            return 0.0
            
        intersection = words_a.intersection(words_b)
        union = words_a.union(words_b)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _detect_common_failure_patterns(self, failures: List[TestFailureData]) -> List[Dict[str, Any]]:
        """Detect common patterns within a group of failures"""
        patterns = []
        
        # Common error message patterns
        error_messages = [f.error_message for f in failures]
        common_error_patterns = self._find_common_text_patterns(error_messages)
        
        for pattern in common_error_patterns:
            patterns.append({
                "type": "error_message_pattern",
                "pattern": pattern,
                "frequency": common_error_patterns[pattern]
            })
            
        # Common file patterns
        test_files = [f.test_file for f in failures]
        common_file_patterns = self._find_common_text_patterns(test_files)
        
        for pattern in common_file_patterns:
            patterns.append({
                "type": "test_file_pattern", 
                "pattern": pattern,
                "frequency": common_file_patterns[pattern]
            })
            
        return patterns
    
    def _build_shared_analysis_context(self, failures: List[TestFailureData], common_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build shared context for batch analysis"""
        return {
            "batch_analysis": True,
            "batch_size": len(failures),
            "common_patterns": common_patterns,
            "failure_types": list(set(f.failure_type for f in failures)),
            "affected_files": list(set(f.test_file for f in failures))
        }
    
    def _find_common_text_patterns(self, texts: List[str]) -> Dict[str, int]:
        """Find common patterns in a list of texts"""
        pattern_counts = {}
        
        for text in texts:
            words = text.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    pattern_counts[word] = pattern_counts.get(word, 0) + 1
                    
        # Return patterns that appear in multiple texts
        return {pattern: count for pattern, count in pattern_counts.items() if count > 1}
    
    def _analyze_temporal_correlations(self, failures: List[TestFailureData]) -> List[Dict[str, Any]]:
        """Analyze temporal correlations between failures"""
        correlations = []
        
        # Sort failures by timestamp
        sorted_failures = sorted(failures, key=lambda f: f.failure_timestamp)
        
        # Look for failures that occurred close in time
        for i in range(len(sorted_failures) - 1):
            current = sorted_failures[i]
            next_failure = sorted_failures[i + 1]
            
            time_diff = (next_failure.failure_timestamp - current.failure_timestamp).total_seconds()
            
            if time_diff < 60:  # Within 1 minute
                correlations.append({
                    "type": "temporal",
                    "failures": [current.test_name, next_failure.test_name],
                    "time_difference_seconds": time_diff,
                    "correlation_strength": max(0.0, 1.0 - (time_diff / 60.0))
                })
                
        return correlations
    
    def _analyze_error_pattern_correlations(self, failures: List[TestFailureData]) -> List[Dict[str, Any]]:
        """Analyze error pattern correlations"""
        correlations = []
        error_groups = {}
        
        # Group failures by error patterns
        for failure in failures:
            error_key = self._extract_error_pattern(failure.error_message)
            if error_key not in error_groups:
                error_groups[error_key] = []
            error_groups[error_key].append(failure)
            
        # Find groups with multiple failures
        for error_pattern, group_failures in error_groups.items():
            if len(group_failures) > 1:
                correlations.append({
                    "type": "error_pattern",
                    "pattern": error_pattern,
                    "failures": [f.test_name for f in group_failures],
                    "correlation_strength": min(1.0, len(group_failures) / len(failures))
                })
                
        return correlations
    
    def _analyze_dependency_correlations(self, failures: List[TestFailureData]) -> List[Dict[str, Any]]:
        """Analyze dependency-related correlations"""
        correlations = []
        
        # Look for import-related failures
        import_failures = [f for f in failures if f.failure_type == 'import']
        
        if len(import_failures) > 1:
            correlations.append({
                "type": "dependency",
                "subtype": "import_failures",
                "failures": [f.test_name for f in import_failures],
                "correlation_strength": len(import_failures) / len(failures)
            })
            
        # Look for file-related failures
        file_failures = [f for f in failures if f.failure_type == 'file_not_found']
        
        if len(file_failures) > 1:
            correlations.append({
                "type": "dependency",
                "subtype": "file_access_failures", 
                "failures": [f.test_name for f in file_failures],
                "correlation_strength": len(file_failures) / len(failures)
            })
            
        return correlations
    
    def _analyze_environmental_correlations(self, failures: List[TestFailureData]) -> List[Dict[str, Any]]:
        """Analyze environment-related correlations"""
        correlations = []
        
        # Check for common environment variables
        env_vars = {}
        for failure in failures:
            failure_env = failure.test_context.get('environment_variables', {})
            for var, value in failure_env.items():
                key = f"{var}={value}"
                if key not in env_vars:
                    env_vars[key] = []
                env_vars[key].append(failure)
                
        # Find environment correlations
        for env_key, env_failures in env_vars.items():
            if len(env_failures) > 1:
                correlations.append({
                    "type": "environmental",
                    "environment_variable": env_key,
                    "failures": [f.test_name for f in env_failures],
                    "correlation_strength": len(env_failures) / len(failures)
                })
                
        return correlations
    
    def _identify_common_root_causes(self, failures: List[TestFailureData]) -> List[Dict[str, Any]]:
        """Identify potential common root causes across failures"""
        root_causes = []
        
        # Analyze failure patterns for common root causes
        failure_types = {}
        for failure in failures:
            if failure.failure_type not in failure_types:
                failure_types[failure.failure_type] = []
            failure_types[failure.failure_type].append(failure)
            
        # Identify dominant failure types as potential root causes
        for failure_type, type_failures in failure_types.items():
            if len(type_failures) > len(failures) * 0.3:  # 30% threshold
                root_causes.append({
                    "type": "failure_type_dominance",
                    "root_cause": failure_type,
                    "affected_failures": [f.test_name for f in type_failures],
                    "confidence": len(type_failures) / len(failures)
                })
                
        # Look for common error message patterns
        common_errors = self._find_common_text_patterns([f.error_message for f in failures])
        for error_pattern, count in common_errors.items():
            if count > len(failures) * 0.25:  # 25% threshold
                root_causes.append({
                    "type": "common_error_pattern",
                    "root_cause": error_pattern,
                    "frequency": count,
                    "confidence": count / len(failures)
                })
                
        return root_causes
    
    def _extract_error_pattern(self, error_message: str) -> str:
        """Extract error pattern from error message"""
        # Remove specific details and keep general pattern
        pattern = error_message.lower()
        
        # Remove file paths
        pattern = re.sub(r'/[^\s]+', '<path>', pattern)
        
        # Remove line numbers
        pattern = re.sub(r'line \d+', 'line <num>', pattern)
        
        # Remove specific values
        pattern = re.sub(r'\d+', '<num>', pattern)
        
        # Remove quotes content
        pattern = re.sub(r"'[^']*'", '<value>', pattern)
        pattern = re.sub(r'"[^"]*"', '<value>', pattern)
        
        return pattern

    # Original private helper methods
    
    def _generate_failure_group_key(self, failure: TestFailureData) -> str:
        """Generate grouping key for related failures"""
        # Group by test file and error type
        error_type = failure.failure_type
        test_module = failure.test_file.split('/')[-1].replace('.py', '')
        
        # Group similar error messages
        error_signature = ""
        if "ImportError" in failure.error_message:
            error_signature = "import_error"
        elif "AssertionError" in failure.error_message:
            error_signature = "assertion_error"
        elif "FileNotFoundError" in failure.error_message:
            error_signature = "file_not_found"
        elif "PermissionError" in failure.error_message:
            error_signature = "permission_error"
        else:
            error_signature = "other_error"
            
        return f"{test_module}_{error_type}_{error_signature}"
        
    def _calculate_failure_priority_score(self, failure: TestFailureData) -> float:
        """Calculate priority score for failure (higher = more important)"""
        score = 0.0
        
        # Critical errors get highest priority
        if any(keyword in failure.error_message.lower() for keyword in 
               ['critical', 'fatal', 'system', 'security']):
            score += 100.0
            
        # Import errors are high priority (block other tests)
        if 'ImportError' in failure.error_message:
            score += 50.0
            
        # Configuration errors are medium-high priority
        if any(keyword in failure.error_message.lower() for keyword in 
               ['config', 'setting', 'environment']):
            score += 30.0
            
        # Test infrastructure failures are high priority
        if any(keyword in failure.test_file.lower() for keyword in 
               ['conftest', 'fixture', 'setup']):
            score += 40.0
            
        # Recent failures get slight priority boost
        time_since_failure = (datetime.now() - failure.failure_timestamp).total_seconds()
        if time_since_failure < 300:  # 5 minutes
            score += 10.0
            
        return score
        
    def _get_failure_priority(self, failure: TestFailureData) -> TestFailurePriorityLevel:
        """Get priority level for failure"""
        score = self._calculate_failure_priority_score(failure)
        
        if score >= 100:
            return TestFailurePriorityLevel.CRITICAL
        elif score >= 50:
            return TestFailurePriorityLevel.HIGH
        elif score >= 20:
            return TestFailurePriorityLevel.MEDIUM
        else:
            return TestFailurePriorityLevel.LOW
            
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
            
    def _generate_rca_summary(self, rca_results: List[RCAResult], pattern_matches: List[PreventionPattern]) -> TestRCASummaryData:
        """Generate summary of RCA analysis results"""
        # Count root cause types
        root_cause_counts = {}
        total_fixes = 0
        total_time = 0
        confidence_scores = []
        critical_issues = []
        
        for result in rca_results:
            for root_cause in result.root_causes:
                cause_type = root_cause.cause_type
                root_cause_counts[cause_type] = root_cause_counts.get(cause_type, 0) + 1
                
                if root_cause.impact_severity == "critical":
                    critical_issues.append(root_cause.description)
                    
            total_fixes += len(result.systematic_fixes)
            total_time += result.total_analysis_time_seconds
            confidence_scores.append(result.rca_confidence_score)
            
        # Sort root causes by frequency
        most_common = sorted(root_cause_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Estimate fix time (rough heuristic)
        estimated_time = total_fixes * 10  # 10 minutes per fix on average
        
        return TestRCASummaryData(
            most_common_root_causes=most_common,
            systematic_fixes_available=total_fixes,
            pattern_matches_found=len(pattern_matches),
            estimated_fix_time_minutes=estimated_time,
            confidence_score=avg_confidence,
            critical_issues=critical_issues
        )
        
    def _generate_recommendations(self, rca_results: List[RCAResult]) -> List[str]:
        """Generate actionable recommendations from RCA results"""
        recommendations = []
        
        # Collect all systematic fixes
        all_fixes = []
        for result in rca_results:
            all_fixes.extend(result.systematic_fixes)
            
        # Group fixes by type and generate recommendations
        fix_types = {}
        for fix in all_fixes:
            fix_type = fix.root_cause.cause_type
            if fix_type not in fix_types:
                fix_types[fix_type] = []
            fix_types[fix_type].append(fix)
            
        # Generate specific recommendations
        for fix_type, fixes in fix_types.items():
            if len(fixes) > 1:
                recommendations.append(f"Address {len(fixes)} {fix_type.value} issues systematically")
            else:
                recommendations.append(f"Fix {fix_type.value}: {fixes[0].fix_description}")
                
        # Add general recommendations
        if len(all_fixes) > 5:
            recommendations.append("Consider implementing automated prevention checks")
            
        if not recommendations:
            recommendations.append("No specific systematic fixes identified - review test failures manually")
            
        return recommendations
        
    def _generate_next_steps(self, rca_results: List[RCAResult], summary: TestRCASummaryData) -> List[str]:
        """Generate next steps for developers"""
        next_steps = []
        
        # Prioritize critical issues
        if summary.critical_issues:
            next_steps.append("Address critical issues first:")
            next_steps.extend([f"  - {issue}" for issue in summary.critical_issues[:3]])
            
        # Suggest systematic approach
        if summary.systematic_fixes_available > 0:
            next_steps.append(f"Apply {summary.systematic_fixes_available} systematic fixes")
            
        # Pattern-based suggestions
        if summary.pattern_matches_found > 0:
            next_steps.append(f"Review {summary.pattern_matches_found} matching prevention patterns")
            
        # Time estimation
        if summary.estimated_fix_time_minutes > 0:
            next_steps.append(f"Estimated fix time: {summary.estimated_fix_time_minutes} minutes")
            
        # Default next steps
        if not next_steps:
            next_steps = [
                "Review test failure details",
                "Check test environment setup",
                "Verify dependencies are installed",
                "Run tests individually to isolate issues"
            ]
            
        return next_steps


# Type aliases for external use
TestFailure = TestFailureData
TestRCASummary = TestRCASummaryData
TestRCAReport = TestRCAReportData
TestFailurePriority = TestFailurePriorityLevel
TestRCAIntegrator = TestRCAIntegrationEngine