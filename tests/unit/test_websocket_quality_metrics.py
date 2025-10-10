"""Unit tests for WebSocket quality metrics."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.beast_mode.observatory.websocket.quality_metrics import (
    QualityMetricsCollector,
    MetricsSnapshot,
    MetricsAggregation,
    QualityThresholds
)
from src.beast_mode.observatory.websocket.health_validator import QualityMetrics


class TestQualityMetricsCollector:
    """Test cases for QualityMetricsCollector."""
    
    @pytest.fixture
    def collector(self):
        """Create QualityMetricsCollector instance."""
        return QualityMetricsCollector(max_history_size=1000)
    
    @pytest.fixture
    def sample_quality_metrics(self):
        """Create sample quality metrics."""
        return QualityMetrics(
            endpoint='/ws/test',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
    
    @pytest.mark.asyncio
    async def test_collect_metrics(self, collector, sample_quality_metrics):
        """Test metrics collection."""
        additional_data = {
            'active_connections': 5,
            'message_count': 100,
            'bytes_sent': 10000,
            'bytes_received': 5000
        }
        
        snapshot = await collector.collect_metrics('/ws/test', sample_quality_metrics, additional_data)
        
        assert isinstance(snapshot, MetricsSnapshot)
        assert snapshot.endpoint == '/ws/test'
        assert snapshot.response_time_ms == 100.0
        assert snapshot.connection_time_ms == 200.0
        assert snapshot.message_latency_ms == 50.0
        assert snapshot.throughput_bytes_per_sec == 1000.0
        assert snapshot.error_rate == 0.01
        assert snapshot.uptime_percentage == 99.0
        assert snapshot.active_connections == 5
        assert snapshot.message_count == 100
        assert snapshot.bytes_sent == 10000
        assert snapshot.bytes_received == 5000
        
        # Check that it's stored in history
        assert '/ws/test' in collector._metrics_history
        assert len(collector._metrics_history['/ws/test']) == 1
    
    @pytest.mark.asyncio
    async def test_get_metrics_history(self, collector, sample_quality_metrics):
        """Test getting metrics history."""
        # Add some metrics
        await collector.collect_metrics('/ws/test', sample_quality_metrics)
        await collector.collect_metrics('/ws/test', sample_quality_metrics)
        await collector.collect_metrics('/ws/test', sample_quality_metrics)
        
        # Get history
        history = await collector.get_metrics_history('/ws/test')
        assert len(history) == 3
        
        # Get limited history
        history = await collector.get_metrics_history('/ws/test', limit=2)
        assert len(history) == 2
        
        # Get history for non-existent endpoint
        history = await collector.get_metrics_history('/ws/nonexistent')
        assert len(history) == 0
    
    @pytest.mark.asyncio
    async def test_get_aggregated_metrics(self, collector, sample_quality_metrics):
        """Test getting aggregated metrics."""
        # Add multiple metrics over time
        for i in range(10):
            metrics = QualityMetrics(
                endpoint='/ws/test',
                response_time_ms=100.0 + i * 10,
                connection_time_ms=200.0 + i * 5,
                message_latency_ms=50.0 + i * 2,
                throughput_bytes_per_sec=1000.0 + i * 100,
                error_rate=0.01 + i * 0.001,
                uptime_percentage=99.0 - i * 0.1
            )
            await collector.collect_metrics('/ws/test', metrics)
        
        # Get aggregated metrics
        aggregation = await collector.get_aggregated_metrics('/ws/test', period_minutes=60)
        
        assert isinstance(aggregation, MetricsAggregation)
        assert aggregation.endpoint == '/ws/test'
        assert aggregation.sample_count == 10
        assert aggregation.avg_response_time_ms > 0
        assert aggregation.min_response_time_ms > 0
        assert aggregation.max_response_time_ms > 0
        assert aggregation.p95_response_time_ms > 0
        assert aggregation.p99_response_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_get_aggregated_metrics_no_data(self, collector):
        """Test getting aggregated metrics with no data."""
        aggregation = await collector.get_aggregated_metrics('/ws/test', period_minutes=60)
        assert aggregation is None
    
    @pytest.mark.asyncio
    async def test_evaluate_quality(self, collector, sample_quality_metrics):
        """Test quality evaluation."""
        # Add some metrics
        for i in range(20):
            await collector.collect_metrics('/ws/test', sample_quality_metrics)
        
        evaluation = await collector.evaluate_quality('/ws/test', period_minutes=60)
        
        assert 'endpoint' in evaluation
        assert 'quality_score' in evaluation
        assert 'status' in evaluation
        assert 'issues' in evaluation
        assert 'recommendations' in evaluation
        assert 'aggregated_metrics' in evaluation
        assert 'thresholds' in evaluation
        
        assert evaluation['endpoint'] == '/ws/test'
        assert 0.0 <= evaluation['quality_score'] <= 1.0
        assert evaluation['status'] in ['excellent', 'good', 'fair', 'poor', 'critical']
    
    @pytest.mark.asyncio
    async def test_evaluate_quality_insufficient_data(self, collector):
        """Test quality evaluation with insufficient data."""
        evaluation = await collector.evaluate_quality('/ws/test', period_minutes=60)
        
        assert evaluation['endpoint'] == '/ws/test'
        assert evaluation['quality_score'] == 0.0
        assert evaluation['status'] == 'insufficient_data'
        assert 'No metrics data available' in evaluation['issues']
    
    @pytest.mark.asyncio
    async def test_detect_quality_degradation(self, collector):
        """Test quality degradation detection."""
        # Add baseline metrics (good performance)
        good_metrics = QualityMetrics(
            endpoint='/ws/test',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        # Add baseline data (older)
        for i in range(20):
            await collector.collect_metrics('/ws/test', good_metrics)
        
        # Add current metrics (poor performance)
        poor_metrics = QualityMetrics(
            endpoint='/ws/test',
            response_time_ms=200.0,  # 2x worse
            connection_time_ms=400.0,  # 2x worse
            message_latency_ms=100.0,  # 2x worse
            throughput_bytes_per_sec=500.0,  # 2x worse
            error_rate=0.05,  # 5x worse
            uptime_percentage=95.0  # Slightly worse
        )
        
        # Add current data (newer)
        for i in range(20):
            await collector.collect_metrics('/ws/test', poor_metrics)
        
        degradations = await collector.detect_quality_degradation('/ws/test', comparison_period_minutes=60)
        
        assert len(degradations) > 0
        
        # Check that degradations are detected
        degradation_types = [d['metric'] for d in degradations]
        assert 'response_time' in degradation_types or 'error_rate' in degradation_types
    
    @pytest.mark.asyncio
    async def test_detect_quality_degradation_insufficient_data(self, collector):
        """Test quality degradation detection with insufficient data."""
        degradations = await collector.detect_quality_degradation('/ws/test', comparison_period_minutes=60)
        assert len(degradations) == 0
    
    def test_update_quality_thresholds(self, collector):
        """Test updating quality thresholds."""
        new_thresholds = QualityThresholds(
            response_time_ms=2000.0,
            connection_time_ms=10000.0,
            message_latency_ms=200.0,
            throughput_bytes_per_sec=2000.0,
            error_rate=0.1,
            uptime_percentage=90.0
        )
        
        collector.update_quality_thresholds(new_thresholds)
        
        assert collector._quality_thresholds.response_time_ms == 2000.0
        assert collector._quality_thresholds.connection_time_ms == 10000.0
        assert collector._quality_thresholds.message_latency_ms == 200.0
        assert collector._quality_thresholds.throughput_bytes_per_sec == 2000.0
        assert collector._quality_thresholds.error_rate == 0.1
        assert collector._quality_thresholds.uptime_percentage == 90.0
    
    def test_get_collection_stats(self, collector, sample_quality_metrics):
        """Test getting collection statistics."""
        # Add some metrics
        collector._metrics_history['/ws/test'] = [sample_quality_metrics] * 5
        collector._metrics_history['/ws/other'] = [sample_quality_metrics] * 3
        
        stats = collector.get_collection_stats()
        
        assert stats['total_metrics_collected'] == 8
        assert stats['endpoints_tracked'] == 2
        assert stats['max_history_size'] == 1000
        assert '/ws/test' in stats['metrics_per_endpoint']
        assert '/ws/other' in stats['metrics_per_endpoint']
        assert stats['metrics_per_endpoint']['/ws/test'] == 5
        assert stats['metrics_per_endpoint']['/ws/other'] == 3
    
    def test_calculate_quality_score(self, collector):
        """Test quality score calculation."""
        # Create aggregation with good metrics
        aggregation = MetricsAggregation(
            endpoint='/ws/test',
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            sample_count=10,
            avg_response_time_ms=500.0,  # Good
            min_response_time_ms=100.0,
            max_response_time_ms=1000.0,
            p95_response_time_ms=800.0,
            p99_response_time_ms=900.0,
            avg_connection_time_ms=1000.0,
            min_connection_time_ms=500.0,
            max_connection_time_ms=2000.0,
            avg_message_latency_ms=50.0,
            min_message_latency_ms=20.0,
            max_message_latency_ms=100.0,
            avg_throughput_bytes_per_sec=2000.0,
            max_throughput_bytes_per_sec=3000.0,
            total_bytes_transferred=100000,
            avg_error_rate=0.01,  # Good
            max_error_rate=0.05,
            avg_uptime_percentage=99.0,  # Good
            min_uptime_percentage=95.0,
            avg_active_connections=5.0,
            max_active_connections=10,
            total_connections=50
        )
        
        score = collector._calculate_quality_score(aggregation)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be good quality
    
    def test_identify_quality_issues(self, collector):
        """Test quality issue identification."""
        # Create aggregation with poor metrics
        aggregation = MetricsAggregation(
            endpoint='/ws/test',
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            sample_count=10,
            avg_response_time_ms=2000.0,  # Exceeds threshold
            min_response_time_ms=1000.0,
            max_response_time_ms=3000.0,
            p95_response_time_ms=2800.0,
            p99_response_time_ms=2900.0,
            avg_connection_time_ms=6000.0,  # Exceeds threshold
            min_connection_time_ms=5000.0,
            max_connection_time_ms=8000.0,
            avg_message_latency_ms=200.0,  # Exceeds threshold
            min_message_latency_ms=100.0,
            max_message_latency_ms=300.0,
            avg_throughput_bytes_per_sec=500.0,
            max_throughput_bytes_per_sec=1000.0,
            total_bytes_transferred=50000,
            avg_error_rate=0.1,  # Exceeds threshold
            max_error_rate=0.2,
            avg_uptime_percentage=80.0,  # Below threshold
            min_uptime_percentage=70.0,
            avg_active_connections=2.0,
            max_active_connections=5,
            total_connections=20
        )
        
        issues = collector._identify_quality_issues(aggregation)
        
        assert len(issues) > 0
        assert any('High response time' in issue for issue in issues)
        assert any('Slow connection time' in issue for issue in issues)
        assert any('High message latency' in issue for issue in issues)
        assert any('High error rate' in issue for issue in issues)
        assert any('Low uptime' in issue for issue in issues)
    
    def test_generate_recommendations(self, collector):
        """Test recommendation generation."""
        # Create aggregation with poor metrics
        aggregation = MetricsAggregation(
            endpoint='/ws/test',
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            sample_count=10,
            avg_response_time_ms=2000.0,  # Poor
            min_response_time_ms=1000.0,
            max_response_time_ms=3000.0,
            p95_response_time_ms=2800.0,
            p99_response_time_ms=2900.0,
            avg_connection_time_ms=6000.0,  # Poor
            min_connection_time_ms=5000.0,
            max_connection_time_ms=8000.0,
            avg_message_latency_ms=200.0,  # Poor
            min_message_latency_ms=100.0,
            max_message_latency_ms=300.0,
            avg_throughput_bytes_per_sec=500.0,
            max_throughput_bytes_per_sec=1000.0,
            total_bytes_transferred=50000,
            avg_error_rate=0.1,  # Poor
            max_error_rate=0.2,
            avg_uptime_percentage=80.0,  # Poor
            min_uptime_percentage=70.0,
            avg_active_connections=2.0,
            max_active_connections=5,
            total_connections=20
        )
        
        issues = ['High response time', 'High error rate', 'Low uptime']
        recommendations = collector._generate_recommendations(aggregation, issues)
        
        assert len(recommendations) > 0
        assert any('optimizing server response time' in rec.lower() for rec in recommendations)
        assert any('error handling' in rec.lower() for rec in recommendations)
        assert any('redundancy' in rec.lower() for rec in recommendations)
    
    def test_percentile_calculation(self, collector):
        """Test percentile calculation."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Test 50th percentile (median)
        p50 = collector._percentile(data, 50)
        assert p50 == 5.5  # Average of 5 and 6
        
        # Test 95th percentile
        p95 = collector._percentile(data, 95)
        assert p95 == 9.55  # Interpolated value
        
        # Test 100th percentile
        p100 = collector._percentile(data, 100)
        assert p100 == 10
        
        # Test empty data
        p_empty = collector._percentile([], 50)
        assert p_empty == 0.0


class TestMetricsSnapshot:
    """Test cases for MetricsSnapshot."""
    
    def test_to_dict(self):
        """Test MetricsSnapshot to_dict method."""
        snapshot = MetricsSnapshot(
            timestamp=datetime.utcnow(),
            endpoint='/ws/test',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0,
            active_connections=5,
            message_count=100,
            bytes_sent=10000,
            bytes_received=5000
        )
        
        snapshot_dict = snapshot.to_dict()
        
        assert snapshot_dict['endpoint'] == '/ws/test'
        assert snapshot_dict['response_time_ms'] == 100.0
        assert snapshot_dict['connection_time_ms'] == 200.0
        assert snapshot_dict['message_latency_ms'] == 50.0
        assert snapshot_dict['throughput_bytes_per_sec'] == 1000.0
        assert snapshot_dict['error_rate'] == 0.01
        assert snapshot_dict['uptime_percentage'] == 99.0
        assert snapshot_dict['active_connections'] == 5
        assert snapshot_dict['message_count'] == 100
        assert snapshot_dict['bytes_sent'] == 10000
        assert snapshot_dict['bytes_received'] == 5000
        assert 'timestamp' in snapshot_dict


class TestMetricsAggregation:
    """Test cases for MetricsAggregation."""
    
    def test_to_dict(self):
        """Test MetricsAggregation to_dict method."""
        aggregation = MetricsAggregation(
            endpoint='/ws/test',
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            sample_count=10,
            avg_response_time_ms=100.0,
            min_response_time_ms=50.0,
            max_response_time_ms=200.0,
            p95_response_time_ms=180.0,
            p99_response_time_ms=195.0,
            avg_connection_time_ms=200.0,
            min_connection_time_ms=100.0,
            max_connection_time_ms=400.0,
            avg_message_latency_ms=50.0,
            min_message_latency_ms=20.0,
            max_message_latency_ms=100.0,
            avg_throughput_bytes_per_sec=1000.0,
            max_throughput_bytes_per_sec=2000.0,
            total_bytes_transferred=50000,
            avg_error_rate=0.01,
            max_error_rate=0.05,
            avg_uptime_percentage=99.0,
            min_uptime_percentage=95.0,
            avg_active_connections=5.0,
            max_active_connections=10,
            total_connections=50
        )
        
        aggregation_dict = aggregation.to_dict()
        
        assert aggregation_dict['endpoint'] == '/ws/test'
        assert aggregation_dict['sample_count'] == 10
        assert 'response_time' in aggregation_dict
        assert 'connection_time' in aggregation_dict
        assert 'message_latency' in aggregation_dict
        assert 'throughput' in aggregation_dict
        assert 'reliability' in aggregation_dict
        assert 'connections' in aggregation_dict
        
        # Check nested structure
        assert aggregation_dict['response_time']['avg_ms'] == 100.0
        assert aggregation_dict['response_time']['min_ms'] == 50.0
        assert aggregation_dict['response_time']['max_ms'] == 200.0


class TestQualityThresholds:
    """Test cases for QualityThresholds."""
    
    def test_to_dict(self):
        """Test QualityThresholds to_dict method."""
        thresholds = QualityThresholds(
            response_time_ms=1000.0,
            connection_time_ms=5000.0,
            message_latency_ms=100.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.05,
            uptime_percentage=95.0
        )
        
        thresholds_dict = thresholds.to_dict()
        
        assert thresholds_dict['response_time_ms'] == 1000.0
        assert thresholds_dict['connection_time_ms'] == 5000.0
        assert thresholds_dict['message_latency_ms'] == 100.0
        assert thresholds_dict['throughput_bytes_per_sec'] == 1000.0
        assert thresholds_dict['error_rate'] == 0.05
        assert thresholds_dict['uptime_percentage'] == 95.0