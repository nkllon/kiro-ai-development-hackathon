"""
Unit tests for ValidationEngine orchestrator.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.websocket_validation.engine import ValidationEngine
from src.websocket_validation.config import ValidationConfig
from src.websocket_validation.models import (
    ValidationStatus, TestStatus, TestResult, ValidationReport
)


class TestValidationEngine:
    """Test cases for ValidationEngine class."""
    
    @pytest.fixture
    def config(self, tmp_path):
        """Create test configuration."""
        return ValidationConfig(evidence_dir=tmp_path / "test_evidence")
    
    @pytest.fixture
    def engine(self, config):
        """Create ValidationEngine instance for testing."""
        with patch('src.websocket_validation.engine.EvidenceCollector'):
            return ValidationEngine(config)
    
    def test_engine_initialization(self, config):
        """Test ValidationEngine initialization."""
        with patch('src.websocket_validation.engine.EvidenceCollector'):
            engine = ValidationEngine(config)
            
            assert engine.config == config
            assert engine.execution_id is not None
            assert engine.logger is not None
            assert engine.evidence_collector is not None
            assert engine.error_handler is not None
            assert len(engine.test_modules) == 4
    
    def test_engine_initialization_default_config(self):
        """Test ValidationEngine initialization with default config."""
        with patch('src.websocket_validation.engine.EvidenceCollector'):
            engine = ValidationEngine()
            
            assert engine.config is not None
            assert isinstance(engine.config, ValidationConfig)
    
    @pytest.mark.asyncio
    async def test_execute_validation_suite_success(self, engine):
        """Test successful validation suite execution."""
        # Mock test module results
        mock_results = [
            TestResult(test_name="test1", status=TestStatus.PASSED),
            TestResult(test_name="test2", status=TestStatus.PASSED)
        ]
        
        # Mock all test modules to return successful results
        for module in engine.test_modules.values():
            module.run_all_tests = AsyncMock(return_value=mock_results)
        
        # Mock evidence collector
        engine.evidence_collector.generate_summary = Mock(return_value={
            "total_items": 10,
            "by_type": {},
            "by_test": {},
            "total_size": 1024,
            "integrity_verified": True
        })
        
        report = await engine.execute_validation_suite()
        
        assert isinstance(report, ValidationReport)
        assert report.execution_id == engine.execution_id
        assert report.overall_status == ValidationStatus.COMPLETED
        assert len(report.test_results) > 0
        assert report.execution_duration > 0
    
    @pytest.mark.asyncio
    async def test_execute_validation_suite_with_failures(self, engine):
        """Test validation suite execution with some test failures."""
        # Mock mixed test results
        mock_results = [
            TestResult(test_name="test1", status=TestStatus.PASSED),
            TestResult(test_name="test2", status=TestStatus.FAILED)
        ]
        
        # Mock test modules
        for module in engine.test_modules.values():
            module.run_all_tests = AsyncMock(return_value=mock_results)
        
        # Mock evidence collector
        engine.evidence_collector.generate_summary = Mock(return_value={
            "total_items": 5,
            "by_type": {},
            "by_test": {},
            "total_size": 512,
            "integrity_verified": True
        })
        
        report = await engine.execute_validation_suite()
        
        assert report.overall_status == ValidationStatus.PARTIAL
        assert len(report.failed_tests) > 0
        assert len(report.passed_tests) > 0
    
    @pytest.mark.asyncio
    async def test_execute_validation_suite_exception(self, engine):
        """Test validation suite execution with exception."""
        # Mock test module to raise exception
        engine.test_modules["system_state"].run_all_tests = AsyncMock(
            side_effect=Exception("Test module failed")
        )
        
        # Mock other modules to return empty results
        for name, module in engine.test_modules.items():
            if name != "system_state":
                module.run_all_tests = AsyncMock(return_value=[])
        
        # Mock evidence collector
        engine.evidence_collector.generate_summary = Mock(return_value={
            "total_items": 0,
            "by_type": {},
            "by_test": {},
            "total_size": 0,
            "integrity_verified": True
        })
        
        report = await engine.execute_validation_suite()
        
        assert report.overall_status == ValidationStatus.FAILED
        # Should have error results from failed phases
        error_results = [r for r in report.test_results if r.status == TestStatus.ERROR]
        assert len(error_results) > 0
    
    def test_run_specific_test_success(self, engine):
        """Test running a specific test successfully."""
        # Mock a test method on one of the modules
        mock_result = TestResult(test_name="specific_test", status=TestStatus.PASSED)
        engine.test_modules["system_state"].specific_test = Mock(return_value=mock_result)
        
        result = engine.run_specific_test("specific_test")
        
        assert result.test_name == "specific_test"
        assert result.status == TestStatus.PASSED
    
    def test_run_specific_test_not_found(self, engine):
        """Test running a non-existent test."""
        result = engine.run_specific_test("nonexistent_test")
        
        assert result.test_name == "nonexistent_test"
        assert result.status == TestStatus.ERROR
        assert "not found" in result.error_details
    
    def test_run_specific_test_exception(self, engine):
        """Test running a specific test that raises exception."""
        # Mock a test method that raises exception
        engine.test_modules["system_state"].failing_test = Mock(
            side_effect=Exception("Test failed")
        )
        
        result = engine.run_specific_test("failing_test")
        
        assert result.test_name == "failing_test"
        assert result.status == TestStatus.ERROR
        assert "Test failed" in result.error_details
    
    def test_get_validation_status_not_started(self, engine):
        """Test getting validation status when not started."""
        status = engine.get_validation_status()
        
        assert status["execution_id"] == engine.execution_id
        assert status["overall_status"] == "not_started"
        assert status["tests_completed"] == 0
        assert status["tests_passed"] == 0
        assert status["tests_failed"] == 0
        assert status["success_rate"] == 0.0
    
    def test_get_validation_status_in_progress(self, engine):
        """Test getting validation status during execution."""
        # Set up engine state as if validation is in progress
        engine.start_time = datetime.utcnow()
        engine.current_report = ValidationReport(
            execution_id=engine.execution_id,
            overall_status=ValidationStatus.IN_PROGRESS,
            test_results=[
                TestResult(test_name="test1", status=TestStatus.PASSED),
                TestResult(test_name="test2", status=TestStatus.FAILED)
            ]
        )
        
        status = engine.get_validation_status()
        
        assert status["overall_status"] == "in_progress"
        assert status["tests_completed"] == 2
        assert status["tests_passed"] == 1
        assert status["tests_failed"] == 1
        assert status["success_rate"] == 50.0
        assert "elapsed_time" in status
    
    def test_generate_evidence_report(self, engine):
        """Test generating evidence report."""
        # Mock evidence collector
        mock_summary = {
            "total_items": 15,
            "by_type": {"log_file": 10, "screenshot": 5},
            "total_size": 2048
        }
        engine.evidence_collector.generate_summary = Mock(return_value=mock_summary)
        
        report = engine.generate_evidence_report()
        
        assert report == mock_summary
        engine.evidence_collector.generate_summary.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_with_retry_success(self, engine):
        """Test retry logic with successful execution."""
        mock_func = AsyncMock(return_value="success")
        
        result = await engine._execute_with_retry(
            mock_func, 
            max_retries=3, 
            phase_name="test_phase"
        )
        
        assert result == "success"
        mock_func.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_with_retry_eventual_success(self, engine):
        """Test retry logic with eventual success after failures."""
        mock_func = AsyncMock(side_effect=[
            Exception("First failure"),
            Exception("Second failure"),
            "success"
        ])
        
        result = await engine._execute_with_retry(
            mock_func,
            max_retries=3,
            phase_name="test_phase"
        )
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    @pytest.mark.asyncio
    async def test_execute_with_retry_max_retries_exceeded(self, engine):
        """Test retry logic when max retries are exceeded."""
        mock_func = AsyncMock(side_effect=Exception("Persistent failure"))
        
        with pytest.raises(Exception, match="Persistent failure"):
            await engine._execute_with_retry(
                mock_func,
                max_retries=2,
                phase_name="test_phase"
            )
        
        assert mock_func.call_count == 3  # Initial attempt + 2 retries
    
    def test_determine_overall_status_no_tests(self, engine):
        """Test overall status determination with no tests."""
        status = engine._determine_overall_status([])
        assert status == ValidationStatus.NOT_STARTED
    
    def test_determine_overall_status_all_passed(self, engine):
        """Test overall status determination with all tests passed."""
        test_results = [
            TestResult(test_name="test1", status=TestStatus.PASSED),
            TestResult(test_name="test2", status=TestStatus.PASSED)
        ]
        
        status = engine._determine_overall_status(test_results)
        assert status == ValidationStatus.COMPLETED
    
    def test_determine_overall_status_all_failed(self, engine):
        """Test overall status determination with all tests failed."""
        test_results = [
            TestResult(test_name="test1", status=TestStatus.FAILED),
            TestResult(test_name="test2", status=TestStatus.ERROR)
        ]
        
        status = engine._determine_overall_status(test_results)
        assert status == ValidationStatus.FAILED
    
    def test_determine_overall_status_mixed(self, engine):
        """Test overall status determination with mixed results."""
        test_results = [
            TestResult(test_name="test1", status=TestStatus.PASSED),
            TestResult(test_name="test2", status=TestStatus.FAILED)
        ]
        
        status = engine._determine_overall_status(test_results)
        assert status == ValidationStatus.PARTIAL