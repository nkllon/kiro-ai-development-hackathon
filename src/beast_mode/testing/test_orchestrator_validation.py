"""
Test Orchestrator Validation

This module was extracted from test_orchestrator.py
as part of RM-DDD compliance refactoring.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import concurrent.futures
import threading
from src.competitive_launch.superiority_engine import SystematicSuperiorityEngine
from src.competitive_launch.failure_recovery import FailureRecoverySystem, FailureType
from src.competitive_launch.launch_execution import LaunchExecutionSystem
from src.devpost_integration.auth_service import DevPostAuthService

def test_systematic_superiority():
    """Test systematic superiority engine"""
    try:
        from src.competitive_launch.superiority_engine import SystematicSuperiorityEngine
        engine = SystematicSuperiorityEngine()
        metrics = engine.generate_superiority_metrics()
        return len(metrics) > 0
    except Exception as e:
        logger.error(f'Systematic superiority test failed: {e}')
        return False

def test_failure_recovery():
    """Test failure recovery system"""
    try:
        from src.competitive_launch.failure_recovery import FailureRecoverySystem, FailureType
        recovery = FailureRecoverySystem()
        failure_id = recovery.detect_failure(failure_type=FailureType.TECHNICAL, description='Test failure', severity=5, impact_areas=['testing'], business_impact='Testing failure recovery')
        return failure_id is not None
    except Exception as e:
        logger.error(f'Failure recovery test failed: {e}')
        return False

def test_launch_execution():
    """Test launch execution system"""
    try:
        from src.competitive_launch.launch_execution import LaunchExecutionSystem
        launch = LaunchExecutionSystem()
        return True
    except Exception as e:
        logger.error(f'Launch execution test failed: {e}')
        return False

def test_devpost_integration():
    """Test DevPost integration"""
    try:
        from src.devpost_integration.auth_service import DevPostAuthService
from src.rm_ddd.core.health import ModuleHealth

        auth = DevPostAuthService()
        return True
    except Exception as e:
        logger.error(f'DevPost integration test failed: {e}')
        return False

def register_test_suite(self, suite: TestSuite):
    """Register a test suite"""
    self.test_suites[suite.suite_id] = suite
    logger.info(f'Registered test suite: {suite.suite_name}')

def run_test_suite(self, suite_id: str) -> List[TestResult]:
    """Run a specific test suite"""
    if suite_id not in self.test_suites:
        raise ValueError(f'Test suite {suite_id} not found')
    suite = self.test_suites[suite_id]
    logger.info(f'Running test suite: {suite.suite_name}')
    results = []
    if suite.parallel:
        results = self._run_tests_parallel(suite)
    else:
        results = self._run_tests_sequential(suite)
    self.test_results.extend(results)
    self.test_history.extend(results)
    return results

def run_all_test_suites(self) -> Dict[str, List[TestResult]]:
    """Run all registered test suites"""
    logger.info('Running all test suites')
    all_results = {}
    for suite_id in self.test_suites:
        try:
            results = self.run_test_suite(suite_id)
            all_results[suite_id] = results
        except Exception as e:
            logger.error(f'Failed to run test suite {suite_id}: {e}')
            all_results[suite_id] = []
    return all_results

def _run_tests_parallel(self, suite: TestSuite) -> List[TestResult]:
    """Run tests in parallel"""
    results = []
    future_to_test = {}
    for i, test_func in enumerate(suite.tests):
        test_id = f'{suite.suite_id}_test_{i}'
        test_name = getattr(test_func, '__name__', f'test_{i}')
        future = self.executor.submit(self._execute_test, test_id, test_name, test_func, suite.timeout, suite.priority, suite.category)
        future_to_test[future] = (test_id, test_name)
    for future in concurrent.futures.as_completed(future_to_test, timeout=suite.timeout + 60):
        test_id, test_name = future_to_test[future]
        try:
            result = future.result()
            results.append(result)
        except Exception as e:
            logger.error(f'Test {test_name} failed with exception: {e}')
            error_result = TestResult(test_id=test_id, test_name=test_name, status=TestStatus.ERROR, start_time=datetime.now(), end_time=datetime.now(), duration=timedelta(0), error_message=str(e), output='', priority=suite.priority, category=suite.category)
            results.append(error_result)
    return results

def _run_tests_sequential(self, suite: TestSuite) -> List[TestResult]:
    """Run tests sequentially"""
    results = []
    for i, test_func in enumerate(suite.tests):
        test_id = f'{suite.suite_id}_test_{i}'
        test_name = getattr(test_func, '__name__', f'test_{i}')
        result = self._execute_test(test_id, test_name, test_func, suite.timeout, suite.priority, suite.category)
        results.append(result)
    return results

def _execute_test(self, test_id: str, test_name: str, test_func: Callable, timeout: int, priority: TestPriority, category: str) -> TestResult:
    """Execute a single test"""
    start_time = datetime.now()
    status = TestStatus.RUNNING
    error_message = None
    output = ''
    try:
        logger.info(f'Executing test: {test_name}')
        result = asyncio.run(asyncio.wait_for(self._run_test_async(test_func), timeout=timeout))
        if result:
            status = TestStatus.PASSED
            output = 'Test passed successfully'
        else:
            status = TestStatus.FAILED
            output = 'Test failed'
    except asyncio.TimeoutError:
        status = TestStatus.TIMEOUT
        error_message = f'Test timed out after {timeout} seconds'
        output = 'Test execution timed out'
    except Exception as e:
        status = TestStatus.ERROR
        error_message = str(e)
        output = f'Test execution error: {e}'
        logger.error(f'Test {test_name} failed: {e}')
    end_time = datetime.now()
    duration = end_time - start_time
    return TestResult(test_id=test_id, test_name=test_name, status=status, start_time=start_time, end_time=end_time, duration=duration, error_message=error_message, output=output, priority=priority, category=category)

def get_test_summary(self) -> Dict[str, Any]:
    """Get test execution summary"""
    if not self.test_results:
        return {'message': 'No tests executed yet'}
    total_tests = len(self.test_results)
    passed_tests = sum((1 for r in self.test_results if r.status == TestStatus.PASSED))
    failed_tests = sum((1 for r in self.test_results if r.status == TestStatus.FAILED))
    error_tests = sum((1 for r in self.test_results if r.status == TestStatus.ERROR))
    timeout_tests = sum((1 for r in self.test_results if r.status == TestStatus.TIMEOUT))
    success_rate = passed_tests / total_tests * 100 if total_tests > 0 else 0
    durations = [r.duration for r in self.test_results if r.duration]
    avg_duration = sum(durations, timedelta(0)) / len(durations) if durations else timedelta(0)
    return {'total_tests': total_tests, 'passed': passed_tests, 'failed': failed_tests, 'errors': error_tests, 'timeouts': timeout_tests, 'success_rate': success_rate, 'average_duration': str(avg_duration), 'test_suites': len(self.test_suites)}

def get_failed_tests(self) -> List[TestResult]:
    """Get list of failed tests"""
    return [r for r in self.test_results if r.status in [TestStatus.FAILED, TestStatus.ERROR, TestStatus.TIMEOUT]]

def get_test_history(self) -> List[TestResult]:
    """Get test execution history"""
    return self.test_history
