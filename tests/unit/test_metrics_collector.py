"""
Unit tests for the metrics collection system.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.beast_mode.monitoring.metrics_collector import (
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    MetricsCollector, MetricType, Metric, MetricSummary
)


class TestMetricsCollector(ReflectiveModule):
    """Test cases for MetricsCollector."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create a metrics collector instance for testing."""
        return MetricsCollector(retention_hours=1, max_metrics_per_type=100)
        
    @pytest.mark.asyncio
    async def test_start_stop_collection(self, metrics_collector):
        """Test starting and stopping metrics collection."""
        assert not metrics_collector.collecting
        
        await metrics_collector.start_collection()
        assert metrics_collector.collecting
        assert metrics_collector.cleanup_task is not None
        
        await metrics_collector.stop_collection()
        assert not metrics_collector.collecting
        
    def test_increment_counter(self, metrics_collector):
        """Test counter increment functionality."""
        # Basic increment
        metrics_collector.increment_counter("test_counter")
        assert metrics_collector.get_counter_value("test_counter") == 1.0
        
        # Increment by specific value
        metrics_collector.increment_counter("test_counter", 5.0)
        assert metrics_collector.get_counter_value("test_counter") == 6.0
        
        # Counter with labels
        metrics_collector.increment_counter("labeled_counter", labels={"type": "error"})
        assert metrics_collector.get_counter_value("labeled_counter", {"type": "error"}) == 1.0
        assert metrics_collector.get_counter_value("labeled_counter") == 0.0  # Different key
        
    def test_set_gauge(self, metrics_collector):
        """Test gauge setting functionality."""
        # Set gauge value
        metrics_collector.set_gauge("test_gauge", 42.5)
        assert metrics_collector.get_gauge_value("test_gauge") == 42.5
        
        # Update gauge value
        metrics_collector.set_gauge("test_gauge", 100.0)
        assert metrics_collector.get_gauge_value("test_gauge") == 100.0
        
        # Gauge with labels
        metrics_collector.set_gauge("labeled_gauge", 25.0, {"component": "redis"})
        assert metrics_collector.get_gauge_value("labeled_gauge", {"component": "redis"}) == 25.0
        
    def test_record_histogram(self, metrics_collector):
        """Test histogram recording functionality."""
        # Record values
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        for value in values:
            metrics_collector.record_histogram("test_histogram", value)
            
        # Get summary
        summary = metrics_collector.get_histogram_summary("test_histogram")
        assert summary is not None
        assert summary.count == 5
        assert summary.min_value == 10.0
        assert summary.max_value == 50.0
        assert summary.avg_value == 30.0
        assert summary.sum_value == 150.0
        
    def test_record_timer(self, metrics_collector):
        """Test timer recording functionality."""
        # Record durations
        durations = [100.0, 200.0, 300.0, 400.0, 500.0]
        for duration in durations:
            metrics_collector.record_timer("test_timer", duration)
            
        # Get summary
        summary = metrics_collector.get_timer_summary("test_timer")
        assert summary is not None
        assert summary.count == 5
        assert summary.min_value == 100.0
        assert summary.max_value == 500.0
        assert summary.avg_value == 300.0
        
    def test_metric_key_creation(self, metrics_collector):
        """Test metric key creation with labels."""
        # No labels
        key = metrics_collector._create_metric_key("test_metric", {})
        assert key == "test_metric"
        
        # With labels
        labels = {"type": "error", "component": "redis"}
        key = metrics_collector._create_metric_key("test_metric", labels)
        assert "test_metric{" in key
        assert "component=redis" in key
        assert "type=error" in key
        
    def test_metric_key_parsing(self, metrics_collector):
        """Test metric key parsing."""
        # No labels
        name, labels = metrics_collector._parse_metric_key("test_metric")
        assert name == "test_metric"
        assert labels == {}
        
        # With labels
        name, labels = metrics_collector._parse_metric_key("test_metric{component=redis,type=error}")
        assert name == "test_metric"
        assert labels == {"component": "redis", "type": "error"}
        
    def test_calculate_summary(self, metrics_collector):
        """Test summary calculation."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        
        summary = metrics_collector._calculate_summary(
            "test_metric", MetricType.HISTOGRAM, values, {}
        )
        
        assert summary.count == 10
        assert summary.min_value == 1.0
        assert summary.max_value == 10.0
        assert summary.avg_value == 5.5
        assert summary.sum_value == 55.0
        
        # Check percentiles
        assert summary.percentiles["p50"] == 5.0  # Median
        assert summary.percentiles["p90"] == 9.0
        assert summary.percentiles["p95"] == 9.0  # Small dataset
        assert summary.percentiles["p99"] == 10.0
        
    def test_get_all_metrics_summary(self, metrics_collector):
        """Test comprehensive metrics summary."""
        # Add various metrics
        metrics_collector.increment_counter("messages_sent", 100)
        metrics_collector.set_gauge("active_connections", 5)
        metrics_collector.record_histogram("response_size", 1024)
        metrics_collector.record_timer("request_duration", 250.0)
        
        summary = metrics_collector.get_all_metrics_summary()
        
        assert "counters" in summary
        assert "gauges" in summary
        assert "histograms" in summary
        assert "timers" in summary
        assert "collection_time" in summary
        
        # Check counter
        counter_keys = list(summary["counters"].keys())
        assert len(counter_keys) > 0
        
        # Check gauge
        gauge_keys = list(summary["gauges"].keys())
        assert len(gauge_keys) > 0
        
    def test_get_performance_report(self, metrics_collector):
        """Test performance report generation."""
        # Set up metrics for KPIs
        metrics_collector.increment_counter("messages_sent", 1000)
        metrics_collector.increment_counter("messages_received", 950)
        metrics_collector.increment_counter("errors", 50)
        metrics_collector.increment_counter("operations", 1000)
        metrics_collector.set_gauge("active_connections", 10)
        
        # Add latency data
        for i in range(100):
            metrics_collector.record_timer("message_latency", 100 + i)
            
        report = metrics_collector.get_performance_report()
        
        assert "timestamp" in report
        assert "summary" in report
        assert "kpis" in report
        
        kpis = report["kpis"]
        
        # Check message throughput
        assert "message_throughput" in kpis
        assert kpis["message_throughput"]["messages_sent"] == 1000
        assert kpis["message_throughput"]["messages_received"] == 950
        
        # Check error rate
        assert "error_rate" in kpis
        assert kpis["error_rate"]["error_rate_percent"] == 5.0  # 50/1000 * 100
        
        # Check latency
        assert "message_latency" in kpis
        assert kpis["message_latency"]["avg_ms"] == 149.5  # Average of 100-199
        
        # Check connections
        assert "connections" in kpis
        assert kpis["connections"]["active_connections"] == 10
        
    @pytest.mark.asyncio
    async def test_cleanup_old_metrics(self, metrics_collector):
        """Test cleanup of old metrics."""
        # Add old metric
        old_metric = Metric(
            name="old_metric",
            type=MetricType.COUNTER,
            value=1.0,
            timestamp=datetime.now() - timedelta(hours=2)  # Older than retention
        )
        
        # Add recent metric
        recent_metric = Metric(
            name="recent_metric",
            type=MetricType.COUNTER,
            value=1.0,
            timestamp=datetime.now()
        )
        
        # Add to metrics storage
        metrics_collector.metrics["old_metric"].append(old_metric)
        metrics_collector.metrics["recent_metric"].append(recent_metric)
        
        # Run cleanup
        await metrics_collector._cleanup_old_metrics()
        
        # Old metric should be removed, recent should remain
        assert len(metrics_collector.metrics["old_metric"]) == 0
        assert len(metrics_collector.metrics["recent_metric"]) == 1
        
    def test_histogram_size_limit(self, metrics_collector):
        """Test histogram size limiting."""
        # Add many values to exceed limit
        for i in range(1500):  # More than the 1000 limit
            metrics_collector.record_histogram("large_histogram", float(i))
            
        # Should be limited to 1000 values
        assert len(metrics_collector.histograms["large_histogram"]) == 1000
        
        # Should keep the most recent values
        values = metrics_collector.histograms["large_histogram"]
        assert min(values) >= 500  # Should have dropped early values
        
    def test_timer_size_limit(self, metrics_collector):
        """Test timer size limiting."""
        # Add many values to exceed limit
        for i in range(1500):  # More than the 1000 limit
            metrics_collector.record_timer("large_timer", float(i))
            
        # Should be limited to 1000 values
        assert len(metrics_collector.timers["large_timer"]) == 1000
        
        # Should keep the most recent values
        values = metrics_collector.timers["large_timer"]
        assert min(values) >= 500  # Should have dropped early values
        
    @pytest.mark.asyncio
    async def test_initialize_default_metrics(self, metrics_collector):
        """Test initialization of default metrics."""
        await metrics_collector._initialize_default_metrics()
        
        # Check that default counters are initialized
        assert metrics_collector.get_counter_value("messages_sent") == 0
        assert metrics_collector.get_counter_value("messages_received") == 0
        assert metrics_collector.get_counter_value("errors") == 0
        assert metrics_collector.get_counter_value("operations") == 0
        
        # Check that default gauges are initialized
        assert metrics_collector.get_gauge_value("active_connections") == 0
        assert metrics_collector.get_gauge_value("active_agents") == 0
        
    def test_empty_summary_handling(self, metrics_collector):
        """Test handling of empty metric collections."""
        # Get summary for non-existent histogram
        summary = metrics_collector.get_histogram_summary("nonexistent")
        assert summary is None
        
        # Get summary for non-existent timer
        summary = metrics_collector.get_timer_summary("nonexistent")
        assert summary is None
        
        # Calculate summary for empty values
        summary = metrics_collector._calculate_summary(
            "empty", MetricType.HISTOGRAM, [], {}
        )
        assert summary.count == 0
        assert summary.min_value == 0
        assert summary.max_value == 0
        assert summary.avg_value == 0

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        assert summary.sum_value == 0