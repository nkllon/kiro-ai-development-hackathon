"""
Unit tests for EvidenceCollector system.
"""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from src.websocket_validation.collectors import EvidenceCollector
from src.websocket_validation.config import ValidationConfig
from src.websocket_validation.models import (
    Evidence, EvidenceType, TestResult, TestStatus
)


class TestEvidenceCollector:
    """Test cases for EvidenceCollector class."""
    
    @pytest.fixture
    def config(self, tmp_path):
        """Create test configuration with temporary evidence directory."""
        return ValidationConfig(
            evidence_dir=tmp_path / "test_evidence",
            encrypt_evidence=False,
            evidence_retention_days=7
        )
    
    @pytest.fixture
    def collector(self, config):
        """Create EvidenceCollector instance for testing."""
        return EvidenceCollector(config)
    
    def test_collector_initialization(self, config):
        """Test EvidenceCollector initialization."""
        collector = EvidenceCollector(config)
        
        assert collector.config == config
        assert collector.evidence_dir == Path(config.evidence_dir)
        assert collector.evidence_dir.exists()
        assert collector.evidence_store == {}
        assert collector.collection_start is None
        assert collector.collection_end is None
    
    def test_evidence_subdirectories_created(self, collector):
        """Test that evidence subdirectories are created."""
        expected_subdirs = [
            "logs", "network_captures", "screenshots", "config_snapshots",
            "test_outputs", "http_responses", "websocket_traces", 
            "code_analysis", "performance_metrics"
        ]
        
        for subdir in expected_subdirs:
            assert (collector.evidence_dir / subdir).exists()
            assert (collector.evidence_dir / subdir).is_dir()
    
    def test_collect_test_evidence(self, collector):
        """Test collecting evidence from test result."""
        test_result = TestResult(
            test_name="test_websocket_connection",
            test_category="system_state",
            status=TestStatus.PASSED,
            execution_time=1.5,
            assertions_passed=3,
            assertions_failed=0
        )
        
        evidence = collector.collect_test_evidence(test_result)
        
        assert isinstance(evidence, Evidence)
        assert evidence.evidence_type == EvidenceType.TEST_OUTPUT
        assert evidence.source_test == "test_websocket_connection"
        assert evidence.evidence_id in collector.evidence_store
        assert evidence.evidence_id in test_result.evidence_ids
        assert collector.collection_start is not None
    
    def test_store_network_capture(self, collector):
        """Test storing network capture data."""
        capture_data = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html>test</html>"
        context = {
            "source_test": "test_endpoint",
            "endpoint": "https://example.com/ws/test",
            "protocol": "HTTP/1.1",
            "format": "raw"
        }
        
        evidence_id = collector.store_network_capture(capture_data, context)
        
        assert evidence_id in collector.evidence_store
        evidence = collector.evidence_store[evidence_id]
        assert evidence.evidence_type == EvidenceType.NETWORK_CAPTURE
        assert evidence.data == capture_data
        assert evidence.metadata["capture_size"] == len(capture_data)
        assert evidence.metadata["endpoint"] == "https://example.com/ws/test"
    
    def test_take_system_screenshot(self, collector):
        """Test taking system screenshot."""
        context = "WebSocket connection test"
        metadata = {"source_test": "test_websocket", "browser": "chrome"}
        
        evidence_id = collector.take_system_screenshot(context, metadata)
        
        assert evidence_id in collector.evidence_store
        evidence = collector.evidence_store[evidence_id]
        assert evidence.evidence_type == EvidenceType.SCREENSHOT
        assert evidence.metadata["context"] == context
        assert evidence.metadata["browser"] == "chrome"
    
    def test_snapshot_configuration(self, collector):
        """Test creating configuration snapshot."""
        config_data = {
            "websocket_enabled": True,
            "proxy_settings": {
                "upstream": "localhost:8888",
                "timeout": 30
            }
        }
        
        evidence_id = collector.snapshot_configuration("cloudflare", config_data)
        
        assert evidence_id in collector.evidence_store
        evidence = collector.evidence_store[evidence_id]
        assert evidence.evidence_type == EvidenceType.CONFIG_SNAPSHOT
        assert evidence.data == config_data
        assert evidence.metadata["config_type"] == "cloudflare"
    
    def test_store_http_response(self, collector):
        """Test storing HTTP response data."""
        evidence_id = collector.store_http_response(
            url="https://example.com/api/test",
            method="GET",
            status_code=200,
            headers={"Content-Type": "application/json"},
            body='{"status": "ok"}',
            response_time=0.5,
            source_test="test_api_endpoint"
        )
        
        assert evidence_id in collector.evidence_store
        evidence = collector.evidence_store[evidence_id]
        assert evidence.evidence_type == EvidenceType.HTTP_RESPONSE
        assert evidence.data["url"] == "https://example.com/api/test"
        assert evidence.data["status_code"] == 200
        assert evidence.metadata["response_time"] == 0.5
    
    def test_store_websocket_trace(self, collector):
        """Test storing WebSocket trace data."""
        messages = [
            {"type": "send", "data": "hello", "timestamp": "2023-01-01T12:00:00Z"},
            {"type": "receive", "data": "world", "timestamp": "2023-01-01T12:00:01Z"}
        ]
        connection_info = {
            "duration": 10.5,
            "status": "closed_normally",
            "close_code": 1000
        }
        
        evidence_id = collector.store_websocket_trace(
            endpoint="wss://example.com/ws/test",
            messages=messages,
            connection_info=connection_info,
            source_test="test_websocket_messaging"
        )
        
        assert evidence_id in collector.evidence_store
        evidence = collector.evidence_store[evidence_id]
        assert evidence.evidence_type == EvidenceType.WEBSOCKET_TRACE
        assert evidence.data["message_count"] == 2
        assert evidence.metadata["connection_duration"] == 10.5
    
    def test_store_log_file(self, collector):
        """Test storing log file content."""
        log_content = """
        2023-01-01 12:00:00 INFO Starting WebSocket server
        2023-01-01 12:00:01 DEBUG Client connected from 192.168.1.100
        2023-01-01 12:00:02 ERROR Connection failed: timeout
        """
        
        evidence_id = collector.store_log_file(
            log_content=log_content,
            log_type="application",
            source_test="test_server_startup"
        )
        
        assert evidence_id in collector.evidence_store
        evidence = collector.evidence_store[evidence_id]
        assert evidence.evidence_type == EvidenceType.LOG_FILE
        assert evidence.data == log_content
        assert evidence.metadata["log_type"] == "application"
        assert evidence.metadata["line_count"] == log_content.count('\n')
    
    def test_get_evidence(self, collector):
        """Test retrieving evidence by ID."""
        # Store some evidence
        test_result = TestResult(test_name="test", status=TestStatus.PASSED)
        evidence = collector.collect_test_evidence(test_result)
        
        # Retrieve evidence
        retrieved = collector.get_evidence(evidence.evidence_id)
        
        assert retrieved is not None
        assert retrieved.evidence_id == evidence.evidence_id
        assert retrieved.source_test == "test"
        
        # Test non-existent evidence
        non_existent = collector.get_evidence("non-existent-id")
        assert non_existent is None
    
    def test_get_evidence_by_test(self, collector):
        """Test retrieving evidence by test name."""
        # Store evidence for multiple tests
        test1 = TestResult(test_name="test1", status=TestStatus.PASSED)
        test2 = TestResult(test_name="test2", status=TestStatus.FAILED)
        test1_again = TestResult(test_name="test1", status=TestStatus.PASSED)
        
        collector.collect_test_evidence(test1)
        collector.collect_test_evidence(test2)
        collector.collect_test_evidence(test1_again)
        
        # Get evidence for test1
        test1_evidence = collector.get_evidence_by_test("test1")
        assert len(test1_evidence) == 2
        assert all(e.source_test == "test1" for e in test1_evidence)
        
        # Get evidence for test2
        test2_evidence = collector.get_evidence_by_test("test2")
        assert len(test2_evidence) == 1
        assert test2_evidence[0].source_test == "test2"
    
    def test_get_evidence_by_type(self, collector):
        """Test retrieving evidence by type."""
        # Store different types of evidence
        collector.collect_test_evidence(TestResult(test_name="test1", status=TestStatus.PASSED))
        collector.store_network_capture(b"data", {"source_test": "test2"})
        collector.take_system_screenshot("context")
        
        # Get test output evidence
        test_evidence = collector.get_evidence_by_type(EvidenceType.TEST_OUTPUT)
        assert len(test_evidence) == 1
        assert test_evidence[0].evidence_type == EvidenceType.TEST_OUTPUT
        
        # Get network capture evidence
        network_evidence = collector.get_evidence_by_type(EvidenceType.NETWORK_CAPTURE)
        assert len(network_evidence) == 1
        assert network_evidence[0].evidence_type == EvidenceType.NETWORK_CAPTURE
        
        # Get screenshot evidence
        screenshot_evidence = collector.get_evidence_by_type(EvidenceType.SCREENSHOT)
        assert len(screenshot_evidence) == 1
        assert screenshot_evidence[0].evidence_type == EvidenceType.SCREENSHOT
    
    def test_verify_evidence_integrity(self, collector):
        """Test evidence integrity verification."""
        # Store evidence
        test_result = TestResult(test_name="test", status=TestStatus.PASSED)
        evidence = collector.collect_test_evidence(test_result)
        
        # Verify integrity
        assert collector.verify_evidence_integrity(evidence.evidence_id) is True
        
        # Corrupt the data and verify integrity fails
        evidence.data = "corrupted data"
        assert collector.verify_evidence_integrity(evidence.evidence_id) is False
        
        # Test non-existent evidence
        assert collector.verify_evidence_integrity("non-existent") is False
    
    def test_generate_summary(self, collector):
        """Test generating evidence summary."""
        # Store various types of evidence
        collector.collect_test_evidence(TestResult(test_name="test1", status=TestStatus.PASSED))
        collector.collect_test_evidence(TestResult(test_name="test2", status=TestStatus.FAILED))
        collector.store_network_capture(b"network data", {"source_test": "test1"})
        collector.take_system_screenshot("screenshot context")
        
        summary = collector.generate_summary()
        
        assert summary["total_items"] == 4
        assert summary["by_type"]["test_output"] == 2
        assert summary["by_type"]["network_capture"] == 1
        assert summary["by_type"]["screenshot"] == 1
        assert summary["by_test"]["test1"] == 2  # test result + network capture
        assert summary["by_test"]["test2"] == 1
        assert summary["total_size"] > 0
        assert summary["integrity_verified"] is True
        assert summary["collection_start"] is not None
        assert summary["collection_end"] is not None
        assert summary["collection_duration"] >= 0
    
    def test_persist_evidence_plain(self, collector):
        """Test persisting evidence to disk in plain format."""
        # Store evidence
        test_result = TestResult(test_name="test_persist", status=TestStatus.PASSED)
        evidence = collector.collect_test_evidence(test_result)
        
        # Check that file was created
        assert evidence.file_path is not None
        assert Path(evidence.file_path).exists()
        
        # Verify file content
        with open(evidence.file_path, 'r') as f:
            file_data = json.load(f)
        
        assert file_data["evidence_id"] == evidence.evidence_id
        assert file_data["evidence_type"] == evidence.evidence_type.value
        assert file_data["source_test"] == evidence.source_test
    
    def test_serialize_evidence_data(self, collector):
        """Test evidence data serialization."""
        # Test string data
        string_data = "test string"
        serialized = collector._serialize_evidence_data(string_data)
        assert serialized == string_data
        
        # Test dict data
        dict_data = {"key": "value", "number": 42}
        serialized = collector._serialize_evidence_data(dict_data)
        assert serialized == dict_data
        
        # Test bytes data
        bytes_data = b"binary data"
        serialized = collector._serialize_evidence_data(bytes_data)
        assert serialized["_type"] == "bytes"
        assert "_data" in serialized
        
        # Test other data types
        other_data = 12345
        serialized = collector._serialize_evidence_data(other_data)
        assert serialized == "12345"
    
    def test_cleanup_old_evidence(self, collector, tmp_path):
        """Test cleaning up old evidence."""
        # Create evidence with old timestamp
        old_evidence = Evidence(
            evidence_type=EvidenceType.TEST_OUTPUT,
            source_test="old_test",
            data="old data"
        )
        # Set timestamp to 10 days ago
        old_evidence.timestamp = datetime.utcnow() - timedelta(days=10)
        
        # Create recent evidence
        recent_evidence = Evidence(
            evidence_type=EvidenceType.TEST_OUTPUT,
            source_test="recent_test",
            data="recent data"
        )
        
        # Store both in collector
        collector.evidence_store[old_evidence.evidence_id] = old_evidence
        collector.evidence_store[recent_evidence.evidence_id] = recent_evidence
        
        # Create fake file for old evidence
        old_file = tmp_path / "old_evidence.json"
        old_file.write_text("old evidence file")
        old_evidence.file_path = str(old_file)
        
        # Clean up with 7-day retention
        cleaned_count = collector.cleanup_old_evidence(retention_days=7)
        
        assert cleaned_count == 1
        assert old_evidence.evidence_id not in collector.evidence_store
        assert recent_evidence.evidence_id in collector.evidence_store
        assert not old_file.exists()
    
    def test_evidence_integrity_hash_calculation(self, collector):
        """Test that evidence integrity hash is calculated correctly."""
        evidence = Evidence(
            evidence_type=EvidenceType.TEST_OUTPUT,
            source_test="test",
            data="test data"
        )
        
        # Hash should be calculated automatically in __post_init__
        assert evidence.integrity_hash != ""
        assert len(evidence.integrity_hash) == 64  # SHA256 hex length
        
        # Same data should produce same hash
        evidence2 = Evidence(
            evidence_type=EvidenceType.TEST_OUTPUT,
            source_test="test",
            data="test data"
        )
        
        assert evidence.integrity_hash == evidence2.integrity_hash
        
        # Different data should produce different hash
        evidence3 = Evidence(
            evidence_type=EvidenceType.TEST_OUTPUT,
            source_test="test",
            data="different data"
        )
        
        assert evidence.integrity_hash != evidence3.integrity_hash