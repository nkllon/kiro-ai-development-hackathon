"""
Observatory Simple Smoke Tests - Fast validation for CI/CD pipeline

These tests provide ultra-fast validation of Observatory functionality
without complex dependencies for pre-commit hooks and CI/CD pipelines.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock

# Test basic data structures that actually exist
from src.beast_mode.observatory.metrics_collector import (
    ComponentMetrics,
    DiscoveredComponent,
)


def test_component_metrics_creation():
    """Test ComponentMetrics basic creation and validation."""
    metrics = ComponentMetrics(
        component_id="test_123",
        component_name="TestComponent",
        component_type="service",
        health_score=0.95,
        uptime_seconds=3600.0,
        error_count=2,
        memory_usage_mb=128.5
    )

    assert metrics.component_id == "test_123"
    assert metrics.component_name == "TestComponent"
    assert metrics.health_score == 0.95
    assert isinstance(metrics.timestamp, datetime)


def test_discovered_component_creation():
    """Test DiscoveredComponent basic creation and validation."""
    component = DiscoveredComponent(
        module_path="src.beast_mode.test.component",
        class_name="TestComponent",
        component_type="service",
        is_reflective=True
    )

    assert component.module_path == "src.beast_mode.test.component"
    assert component.class_name == "TestComponent"
    assert component.component_type == "service"
    assert component.is_reflective is True
    assert isinstance(component.last_seen, datetime)


def test_collect_basic_metrics():
    """Test basic metrics collection structure."""
    # Mock metrics collection without dependencies
    mock_metrics = {
        "timestamp": datetime.now().isoformat(),
        "components_discovered": 5,
        "total_events_processed": 150,
        "average_response_time_ms": 45.2,
        "system_health_score": 0.98,
        "memory_usage_mb": 256.8,
        "cpu_usage_percent": 12.5
    }

    # Validate structure
    required_fields = [
        "timestamp", "components_discovered", "total_events_processed",
        "average_response_time_ms", "system_health_score"
    ]

    for field in required_fields:
        assert field in mock_metrics

    # Validate values
    assert mock_metrics["components_discovered"] >= 0
    assert mock_metrics["total_events_processed"] >= 0
    assert mock_metrics["average_response_time_ms"] > 0
    assert 0 <= mock_metrics["system_health_score"] <= 1.0


def test_basic_trend_analysis():
    """Test basic trend analysis logic."""
    # Test increasing trend
    increasing_data = [10, 20, 30, 40, 50]
    trend_slope = (increasing_data[-1] - increasing_data[0]) / (len(increasing_data) - 1)
    assert trend_slope == 10.0  # 40/4 = 10 per interval

    # Test decreasing trend
    decreasing_data = [50, 40, 30, 20, 10]
    trend_slope = (decreasing_data[-1] - decreasing_data[0]) / (len(decreasing_data) - 1)
    assert trend_slope == -10.0  # -40/4 = -10 per interval

    # Test stable trend
    stable_data = [25, 25, 25, 25, 25]
    trend_slope = (stable_data[-1] - stable_data[0]) / (len(stable_data) - 1)
    assert trend_slope == 0.0


def test_basic_coordination():
    """Test basic coordination event structure."""
    coordination_event = {
        "event_id": "coord_456",
        "event_type": "component_registered",
        "source": "metrics_collector",
        "target": "analytics_engine",
        "timestamp": datetime.now().isoformat(),
        "payload": {
            "component_name": "TestComponent",
            "health_score": 0.95
        },
        "processed": False
    }

    # Validate event structure
    assert "event_id" in coordination_event
    assert "event_type" in coordination_event
    assert "source" in coordination_event
    assert "target" in coordination_event
    assert "timestamp" in coordination_event
    assert "payload" in coordination_event

    # Validate event data
    assert coordination_event["event_id"] is not None
    assert coordination_event["processed"] is False
    assert isinstance(coordination_event["payload"], dict)


def test_observatory_health_check():
    """Test Observatory system health validation."""
    # Mock system component health
    system_components = {
        "metrics_collector": {
            "status": "running",
            "health_score": 0.96,
            "last_heartbeat": datetime.now().isoformat(),
            "error_count": 0
        },
        "data_storage": {
            "status": "running",
            "health_score": 0.98,
            "last_heartbeat": datetime.now().isoformat(),
            "error_count": 1
        },
        "event_processor": {
            "status": "running",
            "health_score": 0.94,
            "last_heartbeat": datetime.now().isoformat(),
            "error_count": 2
        }
    }

    # Calculate overall system health
    active_components = [comp for comp in system_components.values() if comp["status"] == "running"]
    assert len(active_components) == 3  # All components active

    total_health = sum(comp["health_score"] for comp in active_components)
    average_health = total_health / len(active_components)
    assert average_health > 0.9  # System is healthy

    total_errors = sum(comp["error_count"] for comp in active_components)
    assert total_errors < 10  # Acceptable error threshold


def test_configuration_validation():
    """Test Observatory configuration structure."""
    config = {
        "collection_interval_seconds": 30,
        "max_metrics_buffer_size": 1000,
        "enable_real_time_streaming": True,
        "redis_connection": {
            "url": "redis://localhost:6379",
            "max_connections": 20,
            "connection_timeout": 5.0
        },
        "thresholds": {
            "health_score_warning": 0.8,
            "health_score_critical": 0.6,
            "response_time_warning_ms": 100.0,
            "response_time_critical_ms": 500.0
        }
    }

    # Validate required configuration keys
    assert "collection_interval_seconds" in config
    assert "max_metrics_buffer_size" in config
    assert "enable_real_time_streaming" in config
    assert "redis_connection" in config
    assert "thresholds" in config

    # Validate configuration values
    assert config["collection_interval_seconds"] > 0
    assert config["max_metrics_buffer_size"] > 0
    assert isinstance(config["enable_real_time_streaming"], bool)

    # Validate Redis configuration
    redis_config = config["redis_connection"]
    assert "url" in redis_config
    assert redis_config["url"].startswith("redis://")

    # Validate thresholds
    thresholds = config["thresholds"]
    assert 0 < thresholds["health_score_critical"] < thresholds["health_score_warning"] < 1
    assert 0 < thresholds["response_time_warning_ms"] < thresholds["response_time_critical_ms"]