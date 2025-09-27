"""
Unit tests for core data models and types.
"""

import pytest
from datetime import datetime, timedelta
from src.websocket_validation.models import (
    ValidationStatus, TestStatus, EvidenceType, GapAssessmentResult,
    Evidence, TestResult, EndpointResult, HandshakeResult, StabilityResult,
    GapAssessment, Recommendation, ValidationReport
)


class TestEnums:
    """Test cases for enum types."""
    
    def test_validation_status_values(self):
        """Test ValidationStatus enum values."""
        assert ValidationStatus.NOT_STARTED.value == "not_started"
        assert ValidationStatus.IN_PROGRESS.value == "in_progress"
        assert ValidationStatus.COMPLETED.value == "completed"
        assert ValidationStatus.FAILED.value == "failed"
        assert ValidationStatus.PARTIAL.value == "partial"
    
    def test_test_status_values(self):
        """Test TestStatus enum values."""
        assert TestStatus.NOT_STARTED.value == "not_started"
        assert TestStatus.IN_PROGRESS.value == "in_progress"
        assert TestStatus.PASSED.value == "passed"
        assert TestStatus.FAILED.value == "failed"
        assert TestStatus.SKIPPED.value == "skipped"
        assert TestStatus.ERROR.value == "error"
    
    def test_evidence_type_values(self):
        """Test EvidenceType enum values."""
        assert EvidenceType.LOG_FILE.value == "log_file"
        assert EvidenceType.NETWORK_CAPTURE.value == "network_capture"
        assert EvidenceType.SCREENSHOT.value == "screenshot"
        assert EvidenceType.CONFIG_SNAPSHOT.value == "config_snapshot"
        assert EvidenceType.TEST_OUTPUT.value == "test_output"


class TestEvidence:
    """Test cases for Evidence data class."""
    
    def test_evidence_creation(self):
        """Test creating Evidence instance."""
        evidence = Evidence(
            evidence_type=EvidenceType.LOG_FILE,
            source_test="test_websocket_connection",
            data="Test log data"
        )
        
        assert evidence.evidence_id is not None
        assert evidence.timestamp is not None
        assert evidence.evidence_type == EvidenceType.LOG_FILE
        assert evidence.source_test == "test_websocket_connection"
        assert evidence.data == "Test log data"
        assert evidence.integrity_hash != ""
    
    def test_evidence_integrity_hash_string(self):
        """Test integrity hash calculation for string data."""
        evidence = Evidence(data="test data")
        
        # Hash should be calculated automatically
        assert evidence.integrity_hash != ""
        assert len(evidence.integrity_hash) == 64  # SHA256 hex length
    
    def test_evidence_integrity_hash_dict(self):
        """Test integrity hash calculation for dict data."""
        test_data = {"key": "value", "number": 42}
        evidence = Evidence(data=test_data)
        
        assert evidence.integrity_hash != ""
        assert len(evidence.integrity_hash) == 64
    
    def test_evidence_integrity_hash_bytes(self):
        """Test integrity hash calculation for bytes data."""
        test_data = b"binary test data"
        evidence = Evidence(data=test_data)
        
        assert evidence.integrity_hash != ""
        assert len(evidence.integrity_hash) == 64


class TestTestResult:
    """Test cases for TestResult data class."""
    
    def test_test_result_creation(self):
        """Test creating TestResult instance."""
        result = TestResult(
            test_name="test_endpoint_connectivity",
            test_category="system_state",
            status=TestStatus.PASSED
        )
        
        assert result.test_id is not None
        assert result.test_name == "test_endpoint_connectivity"
        assert result.test_category == "system_state"
        assert result.status == TestStatus.PASSED
        assert result.evidence_ids == []
        assert result.metrics == {}
    
    def test_test_result_duration_calculation(self):
        """Test duration calculation from start/end times."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(seconds=5.5)
        
        result = TestResult(
            test_name="test_duration",
            start_time=start_time,
            end_time=end_time
        )
        
        assert abs(result.duration - 5.5) < 0.1
    
    def test_test_result_success_rate(self):
        """Test success rate calculation."""
        result = TestResult(
            test_name="test_success_rate",
            assertions_passed=8,
            assertions_failed=2
        )
        
        assert result.success_rate == 80.0
    
    def test_test_result_success_rate_no_assertions(self):
        """Test success rate with no assertions."""
        result_passed = TestResult(
            test_name="test_passed",
            status=TestStatus.PASSED
        )
        result_failed = TestResult(
            test_name="test_failed",
            status=TestStatus.FAILED
        )
        
        assert result_passed.success_rate == 100.0
        assert result_failed.success_rate == 0.0


class TestEndpointResult:
    """Test cases for EndpointResult data class."""
    
    def test_endpoint_result_creation(self):
        """Test creating EndpointResult instance."""
        result = EndpointResult(
            url="https://example.com/ws/test",
            method="GET",
            status_code=200,
            headers={"Content-Type": "application/json"},
            response_time=0.5
        )
        
        assert result.url == "https://example.com/ws/test"
        assert result.method == "GET"
        assert result.status_code == 200
        assert result.response_time == 0.5
        assert result.is_success is True
    
    def test_endpoint_result_is_success(self):
        """Test is_success property for various status codes."""
        # Successful HTTP responses
        result_200 = EndpointResult(status_code=200)
        result_201 = EndpointResult(status_code=201)
        result_299 = EndpointResult(status_code=299)
        
        assert result_200.is_success is True
        assert result_201.is_success is True
        assert result_299.is_success is True
        
        # WebSocket upgrade
        result_101 = EndpointResult(
            status_code=101,
            websocket_upgrade_success=True
        )
        assert result_101.is_success is True
        
        # Failed responses
        result_404 = EndpointResult(status_code=404)
        result_500 = EndpointResult(status_code=500)
        
        assert result_404.is_success is False
        assert result_500.is_success is False
    
    def test_endpoint_result_is_websocket_upgrade(self):
        """Test is_websocket_upgrade property."""
        result = EndpointResult(
            status_code=101,
            headers={
                "upgrade": "websocket",
                "connection": "upgrade, websocket"
            }
        )
        
        assert result.is_websocket_upgrade is True
        
        # Missing headers
        result_no_headers = EndpointResult(status_code=101)
        assert result_no_headers.is_websocket_upgrade is False


class TestGapAssessment:
    """Test cases for GapAssessment data class."""
    
    def test_gap_assessment_creation(self):
        """Test creating GapAssessment instance."""
        assessment = GapAssessment(
            claims_validated=3,
            claims_refuted=2,
            claims_inconclusive=1,
            documentation_accuracy_percentage=75.0,
            implementation_completeness_percentage=60.0,
            overall_assessment=GapAssessmentResult.MIXED_RESULTS
        )
        
        assert assessment.claims_validated == 3
        assert assessment.claims_refuted == 2
        assert assessment.claims_inconclusive == 1
        assert assessment.total_claims == 6
        assert assessment.overall_assessment == GapAssessmentResult.MIXED_RESULTS
    
    def test_gap_assessment_total_claims(self):
        """Test total_claims property calculation."""
        assessment = GapAssessment(
            claims_validated=5,
            claims_refuted=3,
            claims_inconclusive=2
        )
        
        assert assessment.total_claims == 10
    
    def test_gap_assessment_validation_confidence(self):
        """Test validation_confidence property calculation."""
        assessment = GapAssessment(
            claims_validated=4,
            claims_refuted=2,
            claims_inconclusive=2
        )
        
        # 6 decisive out of 8 total = 75%
        assert assessment.validation_confidence == 75.0
        
        # No claims
        empty_assessment = GapAssessment()
        assert empty_assessment.validation_confidence == 0.0


class TestValidationReport:
    """Test cases for ValidationReport data class."""
    
    def test_validation_report_creation(self):
        """Test creating ValidationReport instance."""
        report = ValidationReport(
            overall_status=ValidationStatus.COMPLETED,
            execution_duration=120.5
        )
        
        assert report.execution_id is not None
        assert report.timestamp is not None
        assert report.overall_status == ValidationStatus.COMPLETED
        assert report.execution_duration == 120.5
        assert report.test_results == []
        assert report.recommendations == []
    
    def test_validation_report_success_rate(self):
        """Test success_rate property calculation."""
        test_results = [
            TestResult(test_name="test1", status=TestStatus.PASSED),
            TestResult(test_name="test2", status=TestStatus.PASSED),
            TestResult(test_name="test3", status=TestStatus.FAILED),
            TestResult(test_name="test4", status=TestStatus.PASSED),
        ]
        
        report = ValidationReport(test_results=test_results)
        
        assert report.success_rate == 75.0  # 3 out of 4 passed
        assert report.total_tests == 4
    
    def test_validation_report_failed_tests(self):
        """Test failed_tests property."""
        test_results = [
            TestResult(test_name="test1", status=TestStatus.PASSED),
            TestResult(test_name="test2", status=TestStatus.FAILED),
            TestResult(test_name="test3", status=TestStatus.FAILED),
            TestResult(test_name="test4", status=TestStatus.PASSED),
        ]
        
        report = ValidationReport(test_results=test_results)
        failed_tests = report.failed_tests
        
        assert len(failed_tests) == 2
        assert all(test.status == TestStatus.FAILED for test in failed_tests)
    
    def test_validation_report_passed_tests(self):
        """Test passed_tests property."""
        test_results = [
            TestResult(test_name="test1", status=TestStatus.PASSED),
            TestResult(test_name="test2", status=TestStatus.FAILED),
            TestResult(test_name="test3", status=TestStatus.PASSED),
        ]
        
        report = ValidationReport(test_results=test_results)
        passed_tests = report.passed_tests
        
        assert len(passed_tests) == 2
        assert all(test.status == TestStatus.PASSED for test in passed_tests)