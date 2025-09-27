"""Unit tests for WebSocket quality metrics collection and analysis."""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import statistics

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.beast_mode.observatory.websocket.quality_metrics import (
    QualityMetricsCollector,
    MetricsSnapshot,
    MetricsAggregation,
    QualityThresholds
)
from src.beast_mode.observatory.websocket.health_validator import QualityMetrics


class TestMetricsSnapshot:
    """Test cases for MetricsSnapshot."""
    
    def test_metrics_snapshot_creation(self):
        """Test MetricsSnapshot creation."""
        snapshot = MetricsSnapshot(
            timestamp=datetime.utcnow(),
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0,
            active_connections=5,
            message_count=100,
            bytes_sent=5000,
            bytes_received=3000
        )
        
        assert snapshot.endpoint == '/ws/emoji-rain'
        assert snapshot.response_time_ms == 100.0
        assert snapshot.connection_time_ms == 200.0
        assert snapshot.message_latency_ms == 50.0
        assert snapshot.throughput_bytes_per_sec == 1000.0
        assert snapshot.error_rate == 0.01
        assert snapshot.uptime_percentage == 99.0
        assert snapshot.active_connections == 5
        assert snapshot.message_count == 100
        assert snapshot.bytes_sent == 5000
        assert snapshot.bytes_received == 3000
        assert isinstance(snapshot.timestamp, datetime)
    
    def test_metrics_snapshot_to_dict(self):
        """Test MetricsSnapshot to_dict method."""
        snapshot = MetricsSnapshot(
            timestamp=datetime.utcnow(),
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0,
            active_connections=5,
            message_count=100,
            bytes_sent=5000,
            bytes_received=3000
        )
        
        data = snapshot.to_dict()
        
        assert data["endpoint"] == '/ws/emoji-rain'
        assert data["response_time_ms"] == 100.0
        assert data["connection_time_ms"] == 200.0
        assert data["message_latency_ms"] == 50.0
        assert data["throughput_bytes_per_sec"] == 1000.0
        assert data["error_rate"] == 0.01
        assert data["uptime_percentage"] == 99.0
        assert data["active_connections"] == 5
        assert data["message_count"] == 100
        assert data["bytes_sent"] == 5000
        assert data["bytes_received"] == 3000
        assert "timestamp" in data


class TestMetricsAggregation:
    """Test cases for MetricsAggregation."""
    
    def test_metrics_aggregation_creation(self):
        """Test MetricsAggregation creation."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=60)
        
        aggregation = MetricsAggregation(
            endpoint='/ws/emoji-rain',
            period_start=start_time,
            period_end=end_time,
            sample_count=100,
            
            # Response time statistics
            avg_response_time_ms=150.0,
            min_response_time_ms=50.0,
            max_response_time_ms=500.0,
            p95_response_time_ms=300.0,
            p99_response_time_ms=450.0,
            
            # Connection time statistics
            avg_connection_time_ms=200.0,
            min_connection_time_ms=100.0,
            max_connection_time_ms=400.0,
            
            # Message latency statistics
            avg_message_latency_ms=75.0,
            min_message_latency_ms=25.0,
            max_message_latency_ms=200.0,
            
            # Throughput statistics
            avg_throughput_bytes_per_sec=1200.0,
            max_throughput_bytes_per_sec=2000.0,
            total_bytes_transferred=7200000,
            
            # Reliability statistics
            avg_error_rate=0.02,
            max_error_rate=0.05,
            avg_uptime_percentage=98.5,
            min_uptime_percentage=95.0,
            
            # Connection statistics
            avg_active_connections=8.5,
            max_active_connections=15,
            total_connections=100
        )
        
        assert aggregation.endpoint == '/ws/emoji-rain'
        assert aggregation.period_start == start_time
        assert aggregation.period_end == end_time
        assert aggregation.sample_count == 100
        assert aggregation.avg_response_time_ms == 150.0
        assert aggregation.min_response_time_ms == 50.0
        assert aggregation.max_response_time_ms == 500.0
        assert aggregation.p95_response_time_ms == 300.0
        assert aggregation.p99_response_time_ms == 450.0
        assert aggregation.avg_connection_time_ms == 200.0
        assert aggregation.avg_message_latency_ms == 75.0
        assert aggregation.avg_throughput_bytes_per_sec == 1200.0
        assert aggregation.total_bytes_transferred == 7200000
        assert aggregation.avg_error_rate == 0.02
        assert aggregation.avg_uptime_percentage == 98.5
        assert aggregation.avg_active_connections == 8.5
        assert aggregation.max_active_connections == 15
        assert aggregation.total_connections == 100
    
    def test_metrics_aggregation_to_dict(self):
        """Test MetricsAggregation to_dict method."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=60)
        
        aggregation = MetricsAggregation(
            endpoint='/ws/emoji-rain',
            period_start=start_time,
            period_end=end_time,
            sample_count=100,
            avg_response_time_ms=150.0,
            min_response_time_ms=50.0,
            max_response_time_ms=500.0,
            p95_response_time_ms=300.0,
            p99_response_time_ms=450.0,
            avg_connection_time_ms=200.0,
            min_connection_time_ms=100.0,
            max_connection_time_ms=400.0,
            avg_message_latency_ms=75.0,
            min_message_latency_ms=25.0,
            max_message_latency_ms=200.0,
            avg_throughput_bytes_per_sec=1200.0,
            max_throughput_bytes_per_sec=2000.0,
            total_bytes_transferred=7200000,
            avg_error_rate=0.02,
            max_error_rate=0.05,
            avg_uptime_percentage=98.5,
            min_uptime_percentage=95.0,
            avg_active_connections=8.5,
            max_active_connections=15,
            total_connections=100
        )
        
        data = aggregation.to_dict()
        
        assert data["endpoint"] == '/ws/emoji-rain'
        assert data["sample_count"] == 100
        assert "response_time" in data
        assert data["response_time"]["avg_ms"] == 150.0
        assert data["response_time"]["min_ms"] == 50.0
        assert data["response_time"]["max_ms"] == 500.0
        assert data["response_time"]["p95_ms"] == 300.0
        assert data["response_time"]["p99_ms"] == 450.0
        assert "connection_time" in data
        assert "message_latency" in data
        assert "throughput" in data
        assert "reliability" in data
        assert "connections" in data


class TestQualityThresholds:
    """Test cases for QualityThresholds."""
    
    def test_default_thresholds(self):
        """Test default quality thresholds."""
        thresholds = QualityThresholds()
        
        assert thresholds.response_time_ms == 1000.0
        assert thresholds.connection_time_ms == 5000.0
        assert thresholds.message_latency_ms == 100.0
        assert thresholds.throughput_bytes_per_sec == 1000.0
        assert thresholds.error_rate == 0.05
        assert thresholds.uptime_percentage == 95.0
    
    def test_custom_thresholds(self):
        """Test custom quality thresholds."""
        thresholds = QualityThresholds(
            response_time_ms=500.0,
            connection_time_ms=2000.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=2000.0,
            error_rate=0.02,
            uptime_percentage=98.0
        )
        
        assert thresholds.response_time_ms == 500.0
        assert thresholds.connection_time_ms == 2000.0
        assert thresholds.message_latency_ms == 50.0
        assert thresholds.throughput_bytes_per_sec == 2000.0
        assert thresholds.error_rate == 0.02
        assert thresholds.uptime_percentage == 98.0
    
    def test_thresholds_to_dict(self):
        """Test QualityThresholds to_dict method."""
        thresholds = QualityThresholds()
        
        data = thresholds.to_dict()
        
        assert data["response_time_ms"] == 1000.0
        assert data["connection_time_ms"] == 5000.0
        assert data["message_latency_ms"] == 100.0
        assert data["throughput_bytes_per_sec"] == 1000.0
        assert data["error_rate"] == 0.05
        assert data["uptime_percentage"] == 95.0


class TestQualityMetricsCollector:
    """Test cases for QualityMetricsCollector."""
    
    @pytest.fixture
    def collector(self):
        """Create a QualityMetricsCollector instance for testing."""
        return QualityMetricsCollector(max_history_size=1000)
    
    def test_initialization(self, collector):
        """Test collector initialization."""
        assert collector.max_history_size == 1000
        assert collector._metrics_history == {}
        assert collector._quality_thresholds is not None
        assert collector._quality_thresholds.response_time_ms == 1000.0
    
    @pytest.mark.asyncio
    async def test_collect_metrics(self, collector):
        """Test collecting metrics."""
        endpoint = '/ws/emoji-rain'
        quality_metrics = QualityMetrics(
            endpoint=endpoint,
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        additional_data = {
            'active_connections': 5,
            'message_count': 100,
            'bytes_sent': 5000,
            'bytes_received': 3000
        }
        
        snapshot = await collector.collect_metrics(endpoint, quality_metrics, additional_data)
        
        assert snapshot.endpoint == endpoint
        assert snapshot.response_time_ms == 100.0
        assert snapshot.connection_time_ms == 200.0
        assert snapshot.message_latency_ms == 50.0
        assert snapshot.throughput_bytes_per_sec == 1000.0
        assert snapshot.error_rate == 0.01
        assert snapshot.uptime_percentage == 99.0
        assert snapshot.active_connections == 5
        assert snapshot.message_count == 100
        assert snapshot.bytes_sent == 5000
        assert snapshot.bytes_received == 3000
        assert isinstance(snapshot.timestamp, datetime)
        
        # Check that it's stored in history
        assert endpoint in collector._metrics_history
        assert len(collector._metrics_history[endpoint]) == 1
        assert collector._metrics_history[endpoint][0] == snapshot
    
    @pytest.mark.asyncio
    async def test_collect_metrics_no_additional_data(self, collector):
        """Test collecting metrics without additional data."""
        endpoint = '/ws/emoji-rain'
        quality_metrics = QualityMetrics(
            endpoint=endpoint,
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        snapshot = await collector.collect_metrics(endpoint, quality_metrics)
        
        assert snapshot.active_connections == 0
        assert snapshot.message_count == 0
        assert snapshot.bytes_sent == 0
        assert snapshot.bytes_received == 0
    
    @pytest.mark.asyncio
    async def test_get_metrics_history(self, collector):
        """Test getting metrics history."""
        endpoint = '/ws/emoji-rain'
        
        # Add some metrics to history
        for i in range(5):
            quality_metrics = QualityMetrics(
                endpoint=endpoint,
                response_time_ms=100.0 + i,
                connection_time_ms=200.0,
                message_latency_ms=50.0,
                throughput_bytes_per_sec=1000.0,
                error_rate=0.01,
                uptime_percentage=99.0
            )
            await collector.collect_metrics(endpoint, quality_metrics)
        
        history = await collector.get_metrics_history(endpoint)
        
        assert len(history) == 5
        assert all(snapshot.endpoint == endpoint for snapshot in history)
    
    @pytest.mark.asyncio
    async def test_get_metrics_history_with_limit(self, collector):
        """Test getting metrics history with limit."""
        endpoint = '/ws/emoji-rain'
        
        # Add some metrics to history
        for i in range(5):
            quality_metrics = QualityMetrics(
                endpoint=endpoint,
                response_time_ms=100.0 + i,
                connection_time_ms=200.0,
                message_latency_ms=50.0,
                throughput_bytes_per_sec=1000.0,
                error_rate=0.01,
                uptime_percentage=99.0
            )
            await collector.collect_metrics(endpoint, quality_metrics)
        
        history = await collector.get_metrics_history(endpoint, limit=3)
        
        assert len(history) == 3
        # Should get the last 3 metrics
        assert history[0].response_time_ms == 102.0
        assert history[1].response_time_ms == 103.0
        assert history[2].response_time_ms == 104.0
    
    @pytest.mark.asyncio
    async def test_get_metrics_history_unknown_endpoint(self, collector):
        """Test getting metrics history for unknown endpoint."""
        endpoint = '/ws/nonexistent'
        
        history = await collector.get_metrics_history(endpoint)
        
        assert len(history) == 0
    
    @pytest.mark.asyncio
    async def test_get_aggregated_metrics(self, collector):
        """Test getting aggregated metrics."""
        endpoint = '/ws/emoji-rain'
        
        # Add metrics with varying values
        response_times = [50.0, 100.0, 150.0, 200.0, 250.0]
        for i, response_time in enumerate(response_times):
            quality_metrics = QualityMetrics(
                endpoint=endpoint,
                response_time_ms=response_time,
                connection_time_ms=200.0 + i * 10,
                message_latency_ms=50.0 + i * 5,
                throughput_bytes_per_sec=1000.0 + i * 100,
                error_rate=0.01 + i * 0.005,
                uptime_percentage=99.0 - i * 0.5
            )
            await collector.collect_metrics(endpoint, quality_metrics)
        
        aggregation = await collector.get_aggregated_metrics(endpoint, period_minutes=60)
        
        assert aggregation is not None
        assert aggregation.endpoint == endpoint
        assert aggregation.sample_count == 5
        assert aggregation.avg_response_time_ms == statistics.mean(response_times)
        assert aggregation.min_response_time_ms == min(response_times)
        assert aggregation.max_response_time_ms == max(response_times)
        assert aggregation.p95_response_time_ms > 0
        assert aggregation.p99_response_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_get_aggregated_metrics_no_data(self, collector):
        """Test getting aggregated metrics with no data."""
        endpoint = '/ws/nonexistent'
        
        aggregation = await collector.get_aggregated_metrics(endpoint, period_minutes=60)
        
        assert aggregation is None
    
    @pytest.mark.asyncio
    async def test_evaluate_quality_excellent(self, collector):
        """Test quality evaluation for excellent performance."""
        endpoint = '/ws/emoji-rain'
        
        # Add excellent metrics
        for _ in range(10):
            quality_metrics = QualityMetrics(
                endpoint=endpoint,
                response_time_ms=50.0,  # Well below threshold
                connection_time_ms=500.0,  # Well below threshold
                message_latency_ms=20.0,  # Well below threshold
                throughput_bytes_per_sec=2000.0,  # Above threshold
                error_rate=0.001,  # Well below threshold
                uptime_percentage=99.9  # Above threshold
            )
            await collector.collect_metrics(endpoint, quality_metrics)
        
        evaluation = await collector.evaluate_quality(endpoint, period_minutes=60)
        
        assert evaluation["endpoint"] == endpoint
        assert evaluation["quality_score"] >= 0.9
        assert evaluation["status"] == "excellent"
        assert len(evaluation["issues"]) == 0
        assert "aggregated_metrics" in evaluation
        assert "thresholds" in evaluation
    
    @pytest.mark.asyncio
    async def test_evaluate_quality_poor(self, collector):
        """Test quality evaluation for poor performance."""
        endpoint = '/ws/emoji-rain'
        
        # Add poor metrics
        for _ in range(10):
            quality_metrics = QualityMetrics(
                endpoint=endpoint,
                response_time_ms=2000.0,  # Above threshold
                connection_time_ms=10000.0,  # Above threshold
                message_latency_ms=500.0,  # Above threshold
                throughput_bytes_per_sec=100.0,  # Below threshold
                error_rate=0.1,  # Above threshold
                uptime_percentage=80.0  # Below threshold
            )
            await collector.collect_metrics(endpoint, quality_metrics)
        
        evaluation = await collector.evaluate_quality(endpoint, period_minutes=60)
        
        assert evaluation["endpoint"] == endpoint
        assert evaluation["quality_score"] < 0.5
        assert evaluation["status"] in ["poor", "critical"]
        assert len(evaluation["issues"]) > 0
        assert len(evaluation["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_evaluate_quality_insufficient_data(self, collector):
        """Test quality evaluation with insufficient data."""
        endpoint = '/ws/nonexistent'
        
        evaluation = await collector.evaluate_quality(endpoint, period_minutes=60)
        
        assert evaluation["endpoint"] == endpoint
        assert evaluation["quality_score"] == 0.0
        assert evaluation["status"] == "insufficient_data"
        assert "No metrics data available" in evaluation["issues"]
        assert len(evaluation["recommendations"]) == 0
    
    @pytest.mark.asyncio
    async def test_detect_quality_degradation(self, collector):
        """Test quality degradation detection."""
        endpoint = '/ws/emoji-rain'
        
        # Add baseline metrics (good performance)
        baseline_time = datetime.utcnow() - timedelta(hours=2)
        for i in range(10):
            quality_metrics = QualityMetrics(
                endpoint=endpoint,
                response_time_ms=100.0,
                connection_time_ms=500.0,
                message_latency_ms=50.0,
                throughput_bytes_per_sec=1000.0,
                error_rate=0.01,
                uptime_percentage=99.0
            )
            # Manually set timestamp to baseline period
            snapshot = await collector.collect_metrics(endpoint, quality_metrics)
            snapshot.timestamp = baseline_time + timedelta(minutes=i)
        
        # Add current metrics (degraded performance)
        for i in range(10):
            quality_metrics = QualityMetrics(
                endpoint=endpoint,
                response_time_ms=300.0,  # 3x worse
                connection_time_ms=500.0,
                message_latency_ms=50.0,
                throughput_bytes_per_sec=1000.0,
                error_rate=0.05,  # 5x worse
                uptime_percentage=99.0
            )
            await collector.collect_metrics(endpoint, quality_metrics)
        
        degradations = await collector.detect_quality_degradation(endpoint, comparison_period_minutes=60)
        
        assert len(degradations) > 0
        assert any(d["metric"] == "response_time" for d in degradations)
        assert any(d["metric"] == "error_rate" for d in degradations)
    
    @pytest.mark.asyncio
    async def test_detect_quality_degradation_insufficient_data(self, collector):
        """Test quality degradation detection with insufficient data."""
        endpoint = '/ws/nonexistent'
        
        degradations = await collector.detect_quality_degradation(endpoint, comparison_period_minutes=60)
        
        assert len(degradations) == 0
    
    def test_update_quality_thresholds(self, collector):
        """Test updating quality thresholds."""
        new_thresholds = QualityThresholds(
            response_time_ms=500.0,
            connection_time_ms=2000.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=2000.0,
            error_rate=0.02,
            uptime_percentage=98.0
        )
        
        collector.update_quality_thresholds(new_thresholds)
        
        assert collector._quality_thresholds.response_time_ms == 500.0
        assert collector._quality_thresholds.connection_time_ms == 2000.0
        assert collector._quality_thresholds.message_latency_ms == 50.0
        assert collector._quality_thresholds.throughput_bytes_per_sec == 2000.0
        assert collector._quality_thresholds.error_rate == 0.02
        assert collector._quality_thresholds.uptime_percentage == 98.0
    
    def test_get_collection_stats(self, collector):
        """Test getting collection statistics."""
        endpoint = '/ws/emoji-rain'
        
        # Add some metrics
        quality_metrics = QualityMetrics(
            endpoint=endpoint,
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        # Manually add to history to test stats
        collector._metrics_history[endpoint] = [quality_metrics]
        
        stats = collector.get_collection_stats()
        
        assert stats["total_metrics_collected"] == 1
        assert stats["endpoints_tracked"] == 1
        assert stats["metrics_per_endpoint"][endpoint] == 1
        assert stats["max_history_size"] == 1000
        assert "quality_thresholds" in stats
    
    def test_calculate_quality_score(self, collector):
        """Test quality score calculation."""
        aggregation = MetricsAggregation(
            endpoint='/ws/emoji-rain',
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            sample_count=1,
            avg_response_time_ms=100.0,  # Good
            min_response_time_ms=100.0,
            max_response_time_ms=100.0,
            p95_response_time_ms=100.0,
            p99_response_time_ms=100.0,
            avg_connection_time_ms=500.0,  # Good
            min_connection_time_ms=500.0,
            max_connection_time_ms=500.0,
            avg_message_latency_ms=50.0,  # Good
            min_message_latency_ms=50.0,
            max_message_latency_ms=50.0,
            avg_throughput_bytes_per_sec=1000.0,  # Good
            max_throughput_bytes_per_sec=1000.0,
            total_bytes_transferred=1000,
            avg_error_rate=0.01,  # Good
            max_error_rate=0.01,
            avg_uptime_percentage=99.0,  # Good
            min_uptime_percentage=99.0,
            avg_active_connections=5.0,
            max_active_connections=5,
            total_connections=1
        )
        
        score = collector._calculate_quality_score(aggregation)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.8  # Should be high for good metrics
    
    def test_identify_quality_issues(self, collector):
        """Test quality issue identification."""
        aggregation = MetricsAggregation(
            endpoint='/ws/emoji-rain',
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            sample_count=1,
            avg_response_time_ms=2000.0,  # Above threshold
            min_response_time_ms=2000.0,
            max_response_time_ms=2000.0,
            p95_response_time_ms=2000.0,
            p99_response_time_ms=2000.0,
            avg_connection_time_ms=10000.0,  # Above threshold
            min_connection_time_ms=10000.0,
            max_connection_time_ms=10000.0,
            avg_message_latency_ms=200.0,  # Above threshold
            min_message_latency_ms=200.0,
            max_message_latency_ms=200.0,
            avg_throughput_bytes_per_sec=100.0,  # Below threshold
            max_throughput_bytes_per_sec=100.0,
            total_bytes_transferred=100,
            avg_error_rate=0.1,  # Above threshold
            max_error_rate=0.1,
            avg_uptime_percentage=80.0,  # Below threshold
            min_uptime_percentage=80.0,
            avg_active_connections=5.0,
            max_active_connections=5,
            total_connections=1
        )
        
        issues = collector._identify_quality_issues(aggregation)
        
        assert len(issues) > 0
        assert any("response time" in issue.lower() for issue in issues)
        assert any("connection time" in issue.lower() for issue in issues)
        assert any("message latency" in issue.lower() for issue in issues)
        assert any("error rate" in issue.lower() for issue in issues)
        assert any("uptime" in issue.lower() for issue in issues)
    
    def test_generate_recommendations(self, collector):
        """Test recommendation generation."""
        aggregation = MetricsAggregation(
            endpoint='/ws/emoji-rain',
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            sample_count=1,
            avg_response_time_ms=2000.0,  # Above threshold
            min_response_time_ms=2000.0,
            max_response_time_ms=2000.0,
            p95_response_time_ms=2000.0,
            p99_response_time_ms=2000.0,
            avg_connection_time_ms=10000.0,  # Above threshold
            min_connection_time_ms=10000.0,
            max_connection_time_ms=10000.0,
            avg_message_latency_ms=200.0,  # Above threshold
            min_message_latency_ms=200.0,
            max_message_latency_ms=200.0,
            avg_throughput_bytes_per_sec=100.0,  # Below threshold
            max_throughput_bytes_per_sec=100.0,
            total_bytes_transferred=100,
            avg_error_rate=0.1,  # Above threshold
            max_error_rate=0.1,
            avg_uptime_percentage=80.0,  # Below threshold
            min_uptime_percentage=80.0,
            avg_active_connections=5.0,
            max_active_connections=5,
            total_connections=1
        )
        
        issues = ["High response time", "High error rate"]
        recommendations = collector._generate_recommendations(aggregation, issues)
        
        assert len(recommendations) > 0
        assert any("response time" in rec.lower() for rec in recommendations)
        assert any("error" in rec.lower() for rec in recommendations)
    
    def test_percentile_calculation(self, collector):
        """Test percentile calculation."""
        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        
        p50 = collector._percentile(data, 50)
        p95 = collector._percentile(data, 95)
        p99 = collector._percentile(data, 99)
        
        assert p50 == 5.5  # Median
        assert p95 == 9.55  # 95th percentile
        assert p99 == 9.91  # 99th percentile
    
    def test_percentile_empty_data(self, collector):
        """Test percentile calculation with empty data."""
        data = []
        
        percentile = collector._percentile(data, 50)
        
        assert percentile == 0.0
    
    def test_log_action(self, collector, capsys):
        """Test JSON logging functionality."""
        collector._log_action("test_action", {"test": "data"})
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.out.strip())
        
        assert log_data["task"] == "2.3"
        assert log_data["action"] == "quality_metrics_test_action"
        assert log_data["status"] == "in_progress"
        assert log_data["details"]["test"] == "data"
        assert "timestamp" in log_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])