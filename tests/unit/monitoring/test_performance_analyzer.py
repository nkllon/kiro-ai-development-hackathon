"""
Unit tests for Performance Analyzer

Tests real-time performance analysis functionality including
latency calculation, throughput measurement, and metrics aggregation.
"""

import asyncio
import pytest
import time
import statistics
from datetime import datetime
from unittest.mock import Mock, patch

from src.beast_mode.observatory.monitoring.performance_analyzer import (
    PerformanceAnalyzer, PerformanceMetrics, MessageEvent
)


class TestPerformanceAnalyzer:
    """Test cases for PerformanceAnalyzer"""

    @pytest.fixture
    def analyzer(self):
        """Create a performance analyzer instance for testing"""
        return PerformanceAnalyzer(max_latency_samples=100, analysis_window_sec=60)

    def test_initialization(self, analyzer):
        """Test performance analyzer initialization"""
        assert analyzer.max_latency_samples == 100
        assert analyzer.analysis_window_sec == 60
        assert len(analyzer._endpoint_metrics) == 0
        assert len(analyzer._sent_messages) == 0
        assert len(analyzer._received_messages) == 0
        assert len(analyzer._message_pairs) == 0
        assert len(analyzer._error_counts) == 0
        assert len(analyzer._total_messages) == 0

    @pytest.mark.asyncio
    async def test_record_message_sent(self, analyzer):
        """Test recording message sent events"""
        endpoint = "test_endpoint"
        timestamp = time.time()
        message_id = "msg_123"
        size = 1024
        
        await analyzer.record_message_sent(endpoint, timestamp, message_id, size)
        
        # Verify message was recorded
        assert endpoint in analyzer._sent_messages
        assert len(analyzer._sent_messages[endpoint]) == 1
        
        event = analyzer._sent_messages[endpoint][0]
        assert event.timestamp == timestamp
        assert event.message_id == message_id
        assert event.size == size
        
        # Verify throughput window
        assert endpoint in analyzer._throughput_windows
        assert timestamp in analyzer._throughput_windows[endpoint]
        
        # Verify bytes window
        assert endpoint in analyzer._bytes_windows
        assert size in analyzer._bytes_windows[endpoint]
        
        # Verify total messages
        assert analyzer._total_messages[endpoint] == 1

    @pytest.mark.asyncio
    async def test_record_message_received(self, analyzer):
        """Test recording message received events"""
        endpoint = "test_endpoint"
        timestamp = time.time()
        message_id = "msg_123"
        size = 512
        
        await analyzer.record_message_received(endpoint, timestamp, message_id, size)
        
        # Verify message was recorded
        assert endpoint in analyzer._received_messages
        assert len(analyzer._received_messages[endpoint]) == 1
        
        event = analyzer._received_messages[endpoint][0]
        assert event.timestamp == timestamp
        assert event.message_id == message_id
        assert event.size == size
        
        # Verify throughput window
        assert endpoint in analyzer._throughput_windows
        assert timestamp in analyzer._throughput_windows[endpoint]
        
        # Verify bytes window
        assert endpoint in analyzer._bytes_windows
        assert size in analyzer._bytes_windows[endpoint]
        
        # Verify total messages
        assert analyzer._total_messages[endpoint] == 1

    @pytest.mark.asyncio
    async def test_calculate_latency_with_message_id(self, analyzer):
        """Test latency calculation with message ID pairing"""
        endpoint = "test_endpoint"
        message_id = "msg_123"
        sent_time = time.time()
        received_time = sent_time + 0.1  # 100ms latency
        
        # Record sent message
        await analyzer.record_message_sent(endpoint, sent_time, message_id, 100)
        
        # Calculate latency
        latency = await analyzer.calculate_latency(endpoint, received_time, message_id)
        
        assert latency == pytest.approx(100.0, rel=1e-2)  # 100ms
        assert len(analyzer._message_pairs[endpoint]) == 1

    @pytest.mark.asyncio
    async def test_calculate_latency_without_message_id(self, analyzer):
        """Test latency calculation without message ID (uses most recent)"""
        endpoint = "test_endpoint"
        sent_time = time.time()
        received_time = sent_time + 0.05  # 50ms latency
        
        # Record sent message
        await analyzer.record_message_sent(endpoint, sent_time, None, 100)
        
        # Calculate latency
        latency = await analyzer.calculate_latency(endpoint, received_time)
        
        assert latency == pytest.approx(50.0, rel=1e-2)  # 50ms
        assert len(analyzer._message_pairs[endpoint]) == 1

    @pytest.mark.asyncio
    async def test_calculate_latency_no_sent_message(self, analyzer):
        """Test latency calculation when no sent message exists"""
        endpoint = "test_endpoint"
        received_time = time.time()
        
        # Calculate latency without any sent messages
        latency = await analyzer.calculate_latency(endpoint, received_time)
        
        assert latency is None
        assert len(analyzer._message_pairs[endpoint]) == 0

    @pytest.mark.asyncio
    async def test_calculate_latency_unreasonable_values(self, analyzer):
        """Test latency calculation with unreasonable values"""
        endpoint = "test_endpoint"
        sent_time = time.time()
        
        # Test negative latency (received before sent)
        received_time_negative = sent_time - 0.1
        await analyzer.record_message_sent(endpoint, sent_time, None, 100)
        latency = await analyzer.calculate_latency(endpoint, received_time_negative)
        assert latency is None
        
        # Test very high latency (>30 seconds)
        received_time_high = sent_time + 35.0
        latency = await analyzer.calculate_latency(endpoint, received_time_high)
        assert latency is None

    @pytest.mark.asyncio
    async def test_get_endpoint_metrics(self, analyzer):
        """Test getting comprehensive endpoint metrics"""
        endpoint = "test_endpoint"
        
        # Set connection start time
        start_time = time.time()
        analyzer.set_connection_start_time(endpoint, start_time)
        
        # Add some message pairs for latency calculation
        sent_time = start_time + 1
        received_time = sent_time + 0.1  # 100ms latency
        
        await analyzer.record_message_sent(endpoint, sent_time, "msg1", 100)
        await analyzer.record_message_received(endpoint, received_time, "msg1", 100)
        
        # Add another pair
        sent_time2 = start_time + 2
        received_time2 = sent_time2 + 0.2  # 200ms latency
        
        await analyzer.record_message_sent(endpoint, sent_time2, "msg2", 200)
        await analyzer.record_message_received(endpoint, received_time2, "msg2", 200)
        
        # Add some errors
        await analyzer.record_error(endpoint, "timeout")
        await analyzer.record_error(endpoint, "connection_lost")
        
        # Wait for throughput calculation
        await asyncio.sleep(0.1)
        
        metrics = await analyzer.get_endpoint_metrics(endpoint)
        
        # Verify metrics
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.endpoint == endpoint
        assert metrics.avg_latency_ms == pytest.approx(150.0, rel=1e-2)  # Average of 100ms and 200ms
        assert metrics.min_latency_ms == pytest.approx(100.0, rel=1e-2)
        assert metrics.max_latency_ms == pytest.approx(200.0, rel=1e-2)
        assert metrics.error_rate == pytest.approx(0.5, rel=1e-2)  # 2 errors / 4 total messages
        assert metrics.connection_uptime_sec > 0
        assert metrics.last_updated > datetime.now() - datetime.now().replace(microsecond=0)

    @pytest.mark.asyncio
    async def test_get_throughput(self, analyzer):
        """Test throughput calculation"""
        endpoint = "test_endpoint"
        current_time = time.time()
        
        # Add messages to throughput window
        for i in range(10):
            await analyzer.record_message_sent(endpoint, current_time - 30 + i, None, 100)
        
        throughput = await analyzer.get_throughput(endpoint)
        
        # Should be approximately 10 messages / 60 seconds = 0.167 msg/sec
        assert throughput == pytest.approx(10.0 / 60.0, rel=1e-1)

    @pytest.mark.asyncio
    async def test_record_error(self, analyzer):
        """Test error recording"""
        endpoint = "test_endpoint"
        error_type = "connection_timeout"
        
        await analyzer.record_error(endpoint, error_type)
        
        assert analyzer._error_counts[endpoint] == 1

    def test_set_connection_start_time(self, analyzer):
        """Test setting connection start time"""
        endpoint = "test_endpoint"
        start_time = time.time()
        
        analyzer.set_connection_start_time(endpoint, start_time)
        
        assert analyzer._connection_start_times[endpoint] == start_time

    def test_set_connection_start_time_default(self, analyzer):
        """Test setting connection start time with default (current time)"""
        endpoint = "test_endpoint"
        
        analyzer.set_connection_start_time(endpoint)
        
        assert endpoint in analyzer._connection_start_times
        assert analyzer._connection_start_times[endpoint] > time.time() - 1

    @pytest.mark.asyncio
    async def test_calculate_latency_stats(self, analyzer):
        """Test latency statistics calculation"""
        endpoint = "test_endpoint"
        
        # Add some message pairs
        pairs = [
            (time.time(), time.time() + 0.01),  # 10ms
            (time.time(), time.time() + 0.02),  # 20ms
            (time.time(), time.time() + 0.03),  # 30ms
            (time.time(), time.time() + 0.04),  # 40ms
            (time.time(), time.time() + 0.05),  # 50ms
        ]
        
        for sent_time, received_time in pairs:
            analyzer._message_pairs[endpoint].append((sent_time, received_time))
        
        stats = await analyzer._calculate_latency_stats(endpoint)
        
        assert stats['min'] == pytest.approx(10.0, rel=1e-2)
        assert stats['max'] == pytest.approx(50.0, rel=1e-2)
        assert stats['avg'] == pytest.approx(30.0, rel=1e-2)
        assert stats['p95'] == pytest.approx(50.0, rel=1e-2)
        assert stats['p99'] == pytest.approx(50.0, rel=1e-2)

    @pytest.mark.asyncio
    async def test_calculate_latency_stats_empty(self, analyzer):
        """Test latency statistics calculation with no data"""
        endpoint = "test_endpoint"
        
        stats = await analyzer._calculate_latency_stats(endpoint)
        
        assert stats['min'] == 0.0
        assert stats['max'] == 0.0
        assert stats['avg'] == 0.0
        assert stats['p95'] == 0.0
        assert stats['p99'] == 0.0

    @pytest.mark.asyncio
    async def test_calculate_throughput(self, analyzer):
        """Test throughput calculation"""
        endpoint = "test_endpoint"
        current_time = time.time()
        
        # Add messages within analysis window
        for i in range(5):
            await analyzer.record_message_sent(endpoint, current_time - 30 + i, None, 100)
        
        throughput_msgs, throughput_bytes = await analyzer._calculate_throughput(endpoint)
        
        # Should be 5 messages / 60 seconds
        assert throughput_msgs == pytest.approx(5.0 / 60.0, rel=1e-1)
        # Should be 500 bytes / 60 seconds
        assert throughput_bytes == pytest.approx(500.0 / 60.0, rel=1e-1)

    @pytest.mark.asyncio
    async def test_calculate_error_rate(self, analyzer):
        """Test error rate calculation"""
        endpoint = "test_endpoint"
        
        # Add some messages and errors
        analyzer._total_messages[endpoint] = 10
        analyzer._error_counts[endpoint] = 2
        
        error_rate = await analyzer._calculate_error_rate(endpoint)
        
        assert error_rate == 0.2  # 2 errors / 10 messages

    @pytest.mark.asyncio
    async def test_calculate_error_rate_no_messages(self, analyzer):
        """Test error rate calculation with no messages"""
        endpoint = "test_endpoint"
        
        error_rate = await analyzer._calculate_error_rate(endpoint)
        
        assert error_rate == 0.0

    @pytest.mark.asyncio
    async def test_calculate_uptime(self, analyzer):
        """Test uptime calculation"""
        endpoint = "test_endpoint"
        start_time = time.time() - 10  # 10 seconds ago
        
        analyzer.set_connection_start_time(endpoint, start_time)
        
        uptime = await analyzer._calculate_uptime(endpoint, time.time())
        
        assert uptime == pytest.approx(10.0, rel=1e-1)

    @pytest.mark.asyncio
    async def test_calculate_uptime_no_start_time(self, analyzer):
        """Test uptime calculation with no start time"""
        endpoint = "test_endpoint"
        
        uptime = await analyzer._calculate_uptime(endpoint, time.time())
        
        assert uptime == 0.0

    def test_get_all_endpoint_metrics(self, analyzer):
        """Test getting all endpoint metrics"""
        # Initially empty
        metrics = analyzer.get_all_endpoint_metrics()
        assert len(metrics) == 0
        
        # Add some metrics
        analyzer._endpoint_metrics["endpoint1"] = PerformanceMetrics(endpoint="endpoint1")
        analyzer._endpoint_metrics["endpoint2"] = PerformanceMetrics(endpoint="endpoint2")
        
        metrics = analyzer.get_all_endpoint_metrics()
        assert len(metrics) == 2
        assert "endpoint1" in metrics
        assert "endpoint2" in metrics

    def test_get_overall_performance_stats(self, analyzer):
        """Test getting overall performance statistics"""
        # Initially empty
        stats = analyzer.get_overall_performance_stats()
        
        assert stats['total_endpoints'] == 0
        assert stats['avg_latency_ms'] == 0.0
        assert stats['total_throughput_msgs_per_sec'] == 0.0
        assert stats['total_throughput_bytes_per_sec'] == 0.0
        assert stats['overall_error_rate'] == 0.0
        
        # Add some metrics
        analyzer._endpoint_metrics["endpoint1"] = PerformanceMetrics(
            endpoint="endpoint1",
            avg_latency_ms=100.0,
            throughput_msgs_per_sec=5.0,
            throughput_bytes_per_sec=1000.0
        )
        analyzer._endpoint_metrics["endpoint2"] = PerformanceMetrics(
            endpoint="endpoint2",
            avg_latency_ms=200.0,
            throughput_msgs_per_sec=3.0,
            throughput_bytes_per_sec=600.0
        )
        
        analyzer._total_messages["endpoint1"] = 10
        analyzer._total_messages["endpoint2"] = 5
        analyzer._error_counts["endpoint1"] = 1
        analyzer._error_counts["endpoint2"] = 1
        
        stats = analyzer.get_overall_performance_stats()
        
        assert stats['total_endpoints'] == 2
        assert stats['avg_latency_ms'] == 150.0  # Average of 100 and 200
        assert stats['total_throughput_msgs_per_sec'] == 8.0  # 5 + 3
        assert stats['total_throughput_bytes_per_sec'] == 1600.0  # 1000 + 600
        assert stats['overall_error_rate'] == pytest.approx(2.0 / 15.0, rel=1e-2)  # 2 errors / 15 messages

    def test_log_action(self, analyzer, capsys):
        """Test JSON logging functionality"""
        analyzer._log_action("test_action", {"key": "value"})
        
        captured = capsys.readouterr()
        log_output = captured.out.strip()
        
        # Should be valid JSON
        import json
        log_data = json.loads(log_output)
        
        assert log_data["task"] == "3.1"
        assert log_data["action"] == "performance_analyzer_test_action"
        assert log_data["status"] == "in_progress"
        assert log_data["details"]["key"] == "value"
        assert "timestamp" in log_data


class TestPerformanceMetrics:
    """Test cases for PerformanceMetrics dataclass"""
    
    def test_performance_metrics_creation(self):
        """Test PerformanceMetrics creation"""
        metrics = PerformanceMetrics(
            endpoint="test_endpoint",
            avg_latency_ms=100.0,
            min_latency_ms=50.0,
            max_latency_ms=200.0,
            p95_latency_ms=180.0,
            p99_latency_ms=195.0,
            throughput_msgs_per_sec=5.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.1,
            connection_uptime_sec=3600.0
        )
        
        assert metrics.endpoint == "test_endpoint"
        assert metrics.avg_latency_ms == 100.0
        assert metrics.min_latency_ms == 50.0
        assert metrics.max_latency_ms == 200.0
        assert metrics.p95_latency_ms == 180.0
        assert metrics.p99_latency_ms == 195.0
        assert metrics.throughput_msgs_per_sec == 5.0
        assert metrics.throughput_bytes_per_sec == 1000.0
        assert metrics.error_rate == 0.1
        assert metrics.connection_uptime_sec == 3600.0
        assert isinstance(metrics.last_updated, datetime)

    def test_performance_metrics_defaults(self):
        """Test PerformanceMetrics default values"""
        metrics = PerformanceMetrics(endpoint="test_endpoint")
        
        assert metrics.endpoint == "test_endpoint"
        assert metrics.avg_latency_ms == 0.0
        assert metrics.min_latency_ms == 0.0
        assert metrics.max_latency_ms == 0.0
        assert metrics.p95_latency_ms == 0.0
        assert metrics.p99_latency_ms == 0.0
        assert metrics.throughput_msgs_per_sec == 0.0
        assert metrics.throughput_bytes_per_sec == 0.0
        assert metrics.error_rate == 0.0
        assert metrics.connection_uptime_sec == 0.0
        assert isinstance(metrics.last_updated, datetime)


class TestMessageEvent:
    """Test cases for MessageEvent dataclass"""
    
    def test_message_event_creation(self):
        """Test MessageEvent creation"""
        timestamp = time.time()
        message_id = "msg_123"
        size = 1024
        
        event = MessageEvent(
            timestamp=timestamp,
            message_id=message_id,
            size=size
        )
        
        assert event.timestamp == timestamp
        assert event.message_id == message_id
        assert event.size == size

    def test_message_event_defaults(self):
        """Test MessageEvent default values"""
        timestamp = time.time()
        
        event = MessageEvent(timestamp=timestamp)
        
        assert event.timestamp == timestamp
        assert event.message_id is None
        assert event.size == 0