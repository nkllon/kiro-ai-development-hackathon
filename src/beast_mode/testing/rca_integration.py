"""
Beast Mode Framework - Test RCA Integration Layer
Implements integration between test failures and RCA engine for systematic analysis
Requirements: 1.1, 1.2, 2.1, 4.1, 4.3
"""

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
    
    def __init__(self, rca_engine: Optional[RCAEngine] = None):
        super().__init__("test_rca_integrator")
        
        # Initialize RCA engine
        self.rca_engine = rca_engine or RCAEngine()
        
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
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for test RCA integration capability"""
        return (not self._degradation_active and 
                self.rca_engine is not None and 
                self.rca_engine.is_healthy())
        
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
        Comprehensive analysis workflow for test failures
        Requirements: 1.1, 1.2, 2.1 - Automatic RCA analysis with comprehensive reporting
        """
        start_time = time.time()
        self.total_test_failures_processed += len(failures)
        
        try:
            self.logger.info(f"Starting RCA analysis for {len(failures)} test failures")
            
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
                
            # Step 4: Perform RCA analysis on each failure
            rca_results = []
            pattern_matches = []
            
            for rca_failure in rca_failures:
                try:
                    # Check for existing patterns first (fast path)
                    existing_patterns = self.rca_engine.match_existing_patterns(rca_failure)
                    pattern_matches.extend(existing_patterns)
                    self.pattern_matches_found += len(existing_patterns)
                    
                    # Perform comprehensive RCA analysis
                    rca_result = self.rca_engine.perform_systematic_rca(rca_failure)
                    rca_results.append(rca_result)
                    self.successful_rca_analyses += 1
                    
                    # Check timeout constraint (30 seconds per requirement 1.4)
                    elapsed_time = time.time() - start_time
                    if elapsed_time > self.analysis_timeout_seconds:
                        self.logger.warning(f"RCA analysis timeout reached: {elapsed_time:.2f}s")
                        break
                        
                except Exception as e:
                    self.logger.error(f"RCA analysis failed for failure {rca_failure.failure_id}: {e}")
                    continue
                    
            # Step 5: Generate comprehensive report
            report = self.generate_comprehensive_report(
                failures, grouped_failures, rca_results, pattern_matches
            )
            
            analysis_time = time.time() - start_time
            self.total_analysis_time += analysis_time
            
            self.logger.info(f"RCA analysis complete: {len(rca_results)} analyses in {analysis_time:.2f}s")
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
        Requirements: 1.3 - Analyze each failure and group related issues
        """
        grouped_failures = {}
        
        try:
            for failure in failures:
                # Generate grouping key based on failure characteristics
                group_key = self._generate_failure_group_key(failure)
                
                if group_key not in grouped_failures:
                    grouped_failures[group_key] = []
                    
                # Limit group size to prevent resource exhaustion
                if len(grouped_failures[group_key]) < self.max_failures_per_group:
                    grouped_failures[group_key].append(failure)
                else:
                    # Create overflow group
                    overflow_key = f"{group_key}_overflow_{len(grouped_failures)}"
                    grouped_failures[overflow_key] = [failure]
                    
            self.logger.info(f"Grouped failures: {[(k, len(v)) for k, v in grouped_failures.items()]}")
            return grouped_failures
            
        except Exception as e:
            self.logger.error(f"Failure grouping failed: {e}")
            # Fallback: each failure in its own group
            return {f"failure_{i}": [failure] for i, failure in enumerate(failures)}
            
    def prioritize_failures(self, failures: List[TestFailureData]) -> List[TestFailureData]:
        """
        Prioritize test failures for analysis order
        Requirements: 1.3 - Multiple test failures with prioritization
        """
        try:
            # Sort failures by priority score (highest first)
            prioritized = sorted(failures, key=self._calculate_failure_priority_score, reverse=True)
            
            priority_info = [(f.test_name, self._get_failure_priority(f).value) for f in prioritized[:5]]
            self.logger.info(f"Top 5 prioritized failures: {priority_info}")
            
            return prioritized
            
        except Exception as e:
            self.logger.error(f"Failure prioritization failed: {e}")
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
            
    # Private helper methods
    
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