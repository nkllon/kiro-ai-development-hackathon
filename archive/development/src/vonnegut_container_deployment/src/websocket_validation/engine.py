"""
ValidationEngine - Central orchestrator for all validation activities.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Type
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import (
    ValidationReport, TestResult, ValidationStatus, TestStatus,
    EvidenceSummary, GapAssessment, Recommendation
)
from .config import ValidationConfig
from .collectors import EvidenceCollector
from .utils import get_logger, ValidationError, ErrorHandler
from .testers import (
    SystemStateTester, CodeAnalysisTester, 
    ConfigurationTester, IntegrationTester
)


class ValidationEngine:
    """
    Central orchestrator for all validation activities.
    
    Coordinates execution of test modules, manages sequencing and dependencies,
    handles error recovery, and provides unified logging and monitoring.
    """
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        """Initialize ValidationEngine with configuration."""
        self.config = config or ValidationConfig.from_env()
        self.logger = get_logger(__name__)
        self.evidence_collector = EvidenceCollector(self.config)
        self.error_handler = ErrorHandler(self.logger)
        
        # Initialize test modules
        self._init_test_modules()
        
        # Execution state
        self.execution_id = str(uuid.uuid4())
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.current_report: Optional[ValidationReport] = None
        
        self.logger.info(f"ValidationEngine initialized with execution_id: {self.execution_id}")
    
    def _init_test_modules(self):
        """Initialize all test modules."""
        try:
            self.system_state_tester = SystemStateTester(self.config, self.evidence_collector)
            self.code_analysis_tester = CodeAnalysisTester(self.config, self.evidence_collector)
            self.configuration_tester = ConfigurationTester(self.config, self.evidence_collector)
            self.integration_tester = IntegrationTester(self.config, self.evidence_collector)
            
            self.test_modules = {
                "system_state": self.system_state_tester,
                "code_analysis": self.code_analysis_tester,
                "configuration": self.configuration_tester,
                "integration": self.integration_tester
            }
            
            self.logger.info("All test modules initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize test modules: {e}")
            raise ValidationError("ENGINE_INIT_ERROR", f"Test module initialization failed: {e}", {})
    
    async def execute_validation_suite(self) -> ValidationReport:
        """
        Execute the complete validation suite.
        
        Returns:
            ValidationReport: Comprehensive validation results
        """
        self.logger.info(f"Starting validation suite execution: {self.execution_id}")
        self.start_time = datetime.utcnow()
        
        # Initialize report
        self.current_report = ValidationReport(
            execution_id=self.execution_id,
            timestamp=self.start_time,
            overall_status=ValidationStatus.IN_PROGRESS,
            configuration=self.config.to_dict()
        )
        
        try:
            # Execute test phases in sequence
            test_results = []
            
            # Phase 1: System State Testing
            self.logger.info("Executing Phase 1: System State Testing")
            system_results = await self._execute_test_phase("system_state")
            test_results.extend(system_results)
            
            # Phase 2: Code Analysis Testing
            self.logger.info("Executing Phase 2: Code Analysis Testing")
            code_results = await self._execute_test_phase("code_analysis")
            test_results.extend(code_results)
            
            # Phase 3: Configuration Testing
            self.logger.info("Executing Phase 3: Configuration Testing")
            config_results = await self._execute_test_phase("configuration")
            test_results.extend(config_results)
            
            # Phase 4: Integration Testing
            self.logger.info("Executing Phase 4: Integration Testing")
            integration_results = await self._execute_test_phase("integration")
            test_results.extend(integration_results)
            
            # Update report with results
            self.current_report.test_results = test_results
            self.current_report.evidence_summary = await self._generate_evidence_summary()
            self.current_report.gap_assessment = await self._generate_gap_assessment(test_results)
            self.current_report.recommendations = await self._generate_recommendations(test_results)
            
            # Determine overall status
            self.current_report.overall_status = self._determine_overall_status(test_results)
            
            self.end_time = datetime.utcnow()
            self.current_report.execution_duration = (self.end_time - self.start_time).total_seconds()
            
            self.logger.info(f"Validation suite completed successfully: {self.execution_id}")
            return self.current_report
            
        except Exception as e:
            self.logger.error(f"Validation suite execution failed: {e}")
            self.current_report.overall_status = ValidationStatus.FAILED
            self.end_time = datetime.utcnow()
            if self.start_time:
                self.current_report.execution_duration = (self.end_time - self.start_time).total_seconds()
            
            # Add error details to report
            error_result = TestResult(
                test_name="validation_suite_execution",
                test_category="framework",
                status=TestStatus.ERROR,
                error_details=str(e)
            )
            self.current_report.test_results.append(error_result)
            
            return self.current_report
    
    async def _execute_test_phase(self, phase_name: str) -> List[TestResult]:
        """
        Execute a specific test phase.
        
        Args:
            phase_name: Name of the test phase to execute
            
        Returns:
            List[TestResult]: Results from the test phase
        """
        if phase_name not in self.test_modules:
            raise ValidationError("INVALID_PHASE", f"Unknown test phase: {phase_name}", {"phase": phase_name})
        
        test_module = self.test_modules[phase_name]
        results = []
        
        try:
            self.logger.info(f"Starting test phase: {phase_name}")
            
            # Execute tests with retry logic
            phase_results = await self._execute_with_retry(
                test_module.run_all_tests,
                max_retries=self.config.max_retries,
                phase_name=phase_name
            )
            
            results.extend(phase_results)
            
            passed_tests = sum(1 for r in phase_results if r.status == TestStatus.PASSED)
            total_tests = len(phase_results)
            
            self.logger.info(f"Test phase {phase_name} completed: {passed_tests}/{total_tests} tests passed")
            
        except Exception as e:
            self.logger.error(f"Test phase {phase_name} failed: {e}")
            
            # Create error result for failed phase
            error_result = TestResult(
                test_name=f"{phase_name}_phase_execution",
                test_category=phase_name,
                status=TestStatus.ERROR,
                error_details=str(e),
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow()
            )
            results.append(error_result)
        
        return results
    
    async def _execute_with_retry(self, func, max_retries: int, phase_name: str, **kwargs):
        """
        Execute function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            max_retries: Maximum number of retry attempts
            phase_name: Name of the phase for logging
            **kwargs: Additional arguments for the function
            
        Returns:
            Function result
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(**kwargs)
                else:
                    return func(**kwargs)
                    
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    wait_time = self.config.retry_backoff * (2 ** attempt)
                    self.logger.warning(
                        f"Phase {phase_name} attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {wait_time} seconds..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Phase {phase_name} failed after {max_retries + 1} attempts: {e}")
        
        raise last_exception
    
    def run_specific_test(self, test_name: str) -> TestResult:
        """
        Run a specific test by name.
        
        Args:
            test_name: Name of the test to run
            
        Returns:
            TestResult: Result of the specific test
        """
        self.logger.info(f"Running specific test: {test_name}")
        
        # Find the test in available modules
        for module_name, module in self.test_modules.items():
            if hasattr(module, test_name):
                try:
                    test_func = getattr(module, test_name)
                    result = test_func()
                    
                    self.logger.info(f"Test {test_name} completed with status: {result.status}")
                    return result
                    
                except Exception as e:
                    self.logger.error(f"Test {test_name} failed: {e}")
                    return TestResult(
                        test_name=test_name,
                        test_category=module_name,
                        status=TestStatus.ERROR,
                        error_details=str(e),
                        start_time=datetime.utcnow(),
                        end_time=datetime.utcnow()
                    )
        
        # Test not found
        self.logger.error(f"Test {test_name} not found in any module")
        return TestResult(
            test_name=test_name,
            test_category="unknown",
            status=TestStatus.ERROR,
            error_details=f"Test {test_name} not found",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )
    
    def get_validation_status(self) -> Dict[str, Any]:
        """
        Get current validation status.
        
        Returns:
            Dict containing current validation status information
        """
        status = {
            "execution_id": self.execution_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "overall_status": self.current_report.overall_status.value if self.current_report else "not_started",
            "tests_completed": len(self.current_report.test_results) if self.current_report else 0,
            "tests_passed": len(self.current_report.passed_tests) if self.current_report else 0,
            "tests_failed": len(self.current_report.failed_tests) if self.current_report else 0,
            "success_rate": self.current_report.success_rate if self.current_report else 0.0
        }
        
        if self.start_time:
            current_time = self.end_time or datetime.utcnow()
            status["elapsed_time"] = (current_time - self.start_time).total_seconds()
        
        return status
    
    def generate_evidence_report(self) -> Dict[str, Any]:
        """
        Generate evidence report.
        
        Returns:
            Dict containing evidence collection summary
        """
        return self.evidence_collector.generate_summary()
    
    async def _generate_evidence_summary(self) -> EvidenceSummary:
        """Generate summary of collected evidence."""
        evidence_data = self.evidence_collector.generate_summary()
        
        return EvidenceSummary(
            total_evidence_items=evidence_data.get("total_items", 0),
            evidence_by_type=evidence_data.get("by_type", {}),
            evidence_by_test=evidence_data.get("by_test", {}),
            total_size_bytes=evidence_data.get("total_size", 0),
            integrity_verified=evidence_data.get("integrity_verified", True),
            collection_start=evidence_data.get("collection_start"),
            collection_end=evidence_data.get("collection_end")
        )
    
    async def _generate_gap_assessment(self, test_results: List[TestResult]) -> GapAssessment:
        """Generate gap assessment based on test results."""
        # This is a simplified implementation - would be enhanced with actual analysis
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.status == TestStatus.PASSED)
        failed_tests = sum(1 for r in test_results if r.status == TestStatus.FAILED)
        
        # Calculate implementation completeness
        implementation_completeness = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Determine overall assessment
        if implementation_completeness >= 90:
            overall_assessment = "claims_refuted"  # High implementation = gap analysis wrong
            claims_refuted = total_tests
            claims_validated = 0
        elif implementation_completeness <= 30:
            overall_assessment = "claims_validated"  # Low implementation = gap analysis correct
            claims_validated = total_tests
            claims_refuted = 0
        else:
            overall_assessment = "mixed_results"
            claims_validated = failed_tests
            claims_refuted = passed_tests
        
        return GapAssessment(
            claims_validated=claims_validated,
            claims_refuted=claims_refuted,
            claims_inconclusive=0,
            documentation_accuracy_percentage=implementation_completeness,
            implementation_completeness_percentage=implementation_completeness,
            overall_assessment=overall_assessment
        )
    
    async def _generate_recommendations(self, test_results: List[TestResult]) -> List[Recommendation]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        failed_tests = [r for r in test_results if r.status == TestStatus.FAILED]
        
        if failed_tests:
            recommendations.append(Recommendation(
                title="Address Failed Tests",
                description=f"There are {len(failed_tests)} failed tests that need attention",
                priority="high",
                category="implementation",
                action_items=[
                    f"Investigate and fix: {test.test_name}" for test in failed_tests[:5]
                ]
            ))
        
        # Add more sophisticated recommendation logic here
        
        return recommendations
    
    def _determine_overall_status(self, test_results: List[TestResult]) -> ValidationStatus:
        """Determine overall validation status based on test results."""
        if not test_results:
            return ValidationStatus.NOT_STARTED
        
        failed_tests = sum(1 for r in test_results if r.status in [TestStatus.FAILED, TestStatus.ERROR])
        passed_tests = sum(1 for r in test_results if r.status == TestStatus.PASSED)
        
        if failed_tests == 0:
            return ValidationStatus.COMPLETED
        elif passed_tests == 0:
            return ValidationStatus.FAILED
        else:
            return ValidationStatus.PARTIAL