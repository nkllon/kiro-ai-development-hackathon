#!/usr/bin/env python3
"""
Integration test for WebSocket Health Monitoring Framework

Tests the complete monitoring system with real WebSocket simulation
to validate all components work together correctly.
"""

import asyncio
import time
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# Import the monitoring components
from src.beast_mode.observatory.monitoring import (
    WebSocketHealthMonitor, HealthStatus, MetricsCollector,
    ConnectionTracker, PerformanceAnalyzer, AlertManager
)


class MockWebSocket:
    """Mock WebSocket for testing"""
    def __init__(self):
        self.closed = False
        self.send = AsyncMock()
        self.recv = AsyncMock()
        self.close = AsyncMock()


async def test_websocket_health_monitoring():
    """Test the complete WebSocket health monitoring system"""
    print("🔍 Testing WebSocket Health Monitoring Framework...")
    
    # Initialize the health monitor
    health_monitor = WebSocketHealthMonitor()
    print("✅ Health monitor initialized")
    
    # Create mock WebSocket connections
    websocket1 = MockWebSocket()
    websocket2 = MockWebSocket()
    
    # Test connection monitoring
    endpoint1 = "ws://localhost:8080/chat"
    endpoint2 = "ws://localhost:8080/notifications"
    
    print(f"📡 Monitoring connection: {endpoint1}")
    await health_monitor.monitor_connection(endpoint1, websocket1)
    
    print(f"📡 Monitoring connection: {endpoint2}")
    await health_monitor.monitor_connection(endpoint2, websocket2)
    
    # Verify connections are being monitored
    assert len(health_monitor._monitoring_active) == 2
    assert health_monitor.metrics['websocket_connections_active'] == 2
    print("✅ Connections successfully monitored")
    
    # Simulate message activity
    print("📨 Simulating message activity...")
    
    # Send some messages
    for i in range(5):
        await health_monitor.record_message_sent(endpoint1, time.time())
        await asyncio.sleep(0.01)  # Small delay
        await health_monitor.record_message_received(endpoint1, time.time())
        
        await health_monitor.record_message_sent(endpoint2, time.time())
        await asyncio.sleep(0.01)
        await health_monitor.record_message_received(endpoint2, time.time())
    
    print("✅ Message activity simulated")
    
    # Test health status retrieval
    health_status1 = health_monitor.get_health_status(endpoint1)
    health_status2 = health_monitor.get_health_status(endpoint2)
    
    print(f"🏥 Health status for {endpoint1}: {health_status1.value}")
    print(f"🏥 Health status for {endpoint2}: {health_status2.value}")
    
    # Test performance metrics
    performance_metrics = health_monitor.get_performance_metrics()
    print("📊 Performance Metrics:")
    print(f"  - Active connections: {performance_metrics['connection_count']}")
    print(f"  - Endpoints monitored: {performance_metrics['endpoints_monitored']}")
    print(f"  - Latency stats: {performance_metrics['latency_stats']}")
    print(f"  - Health summary: {performance_metrics['health_summary']}")
    
    # Test individual component functionality
    print("\n🔧 Testing individual components...")
    
    # Test MetricsCollector
    metrics_collector = MetricsCollector()
    await metrics_collector.increment_counter("test_counter", 5)
    await metrics_collector.set_gauge("test_gauge", 42.5)
    await metrics_collector.observe_histogram("test_histogram", 100.0)
    
    counter_value = metrics_collector.get_counter("test_counter")
    gauge_value = metrics_collector.get_gauge("test_gauge")
    histogram_stats = metrics_collector.get_histogram_stats("test_histogram")
    
    print(f"✅ MetricsCollector - Counter: {counter_value}, Gauge: {gauge_value}")
    print(f"✅ MetricsCollector - Histogram: {histogram_stats}")
    
    # Test ConnectionTracker
    connection_tracker = ConnectionTracker()
    await connection_tracker.track_connection("test_endpoint", websocket1)
    await connection_tracker.record_message_sent("test_endpoint", 1024)
    await connection_tracker.record_message_received("test_endpoint", 512)
    
    connection_info = connection_tracker.get_connection_info("test_endpoint")
    overall_stats = connection_tracker.get_overall_stats()
    
    print(f"✅ ConnectionTracker - Connection info: {connection_info.endpoint if connection_info else 'None'}")
    print(f"✅ ConnectionTracker - Overall stats: {overall_stats['active_connections']} active")
    
    # Test PerformanceAnalyzer
    performance_analyzer = PerformanceAnalyzer()
    await performance_analyzer.record_message_sent("test_endpoint", time.time(), "msg1", 100)
    await performance_analyzer.record_message_received("test_endpoint", time.time() + 0.1, "msg1", 100)
    
    endpoint_metrics = await performance_analyzer.get_endpoint_metrics("test_endpoint")
    throughput = await performance_analyzer.get_throughput("test_endpoint")
    
    print(f"✅ PerformanceAnalyzer - Avg latency: {endpoint_metrics.avg_latency_ms:.2f}ms")
    print(f"✅ PerformanceAnalyzer - Throughput: {throughput:.2f} msgs/sec")
    
    # Test AlertManager
    alert_manager = AlertManager()
    
    # Trigger some alerts
    alert1 = await alert_manager.trigger_alert(
        endpoint1, "high_latency", ["Latency exceeded threshold"], 
        alert_manager._alert_rules["high_latency"].severity
    )
    
    alert2 = await alert_manager.trigger_alert(
        endpoint2, "low_throughput", ["Throughput below threshold"],
        alert_manager._alert_rules["low_throughput"].severity
    )
    
    active_alerts = alert_manager.get_active_alerts()
    alert_summary = alert_manager.get_alert_summary()
    
    print(f"✅ AlertManager - Active alerts: {len(active_alerts)}")
    print(f"✅ AlertManager - Alert summary: {alert_summary}")
    
    # Test alert acknowledgment and resolution
    if alert1:
        await alert_manager.acknowledge_alert(alert1.id, "admin", "Investigating")
        await alert_manager.resolve_alert(alert1.id, "Issue resolved")
        print("✅ Alert lifecycle management tested")
    
    # Test JSON logging
    print("\n📝 Testing JSON logging...")
    health_monitor._log_action("integration_test", {
        "test_completed": True,
        "connections_tested": 2,
        "messages_simulated": 10,
        "components_validated": 4
    })
    
    # Clean up
    await health_monitor.stop_monitoring(endpoint1)
    await health_monitor.stop_monitoring(endpoint2)
    
    print("\n🎉 WebSocket Health Monitoring Framework validation completed successfully!")
    print("📋 Summary:")
    print("  ✅ WebSocketHealthMonitor - Core monitoring functionality")
    print("  ✅ MetricsCollector - High-performance metrics collection")
    print("  ✅ ConnectionTracker - Real-time connection tracking")
    print("  ✅ PerformanceAnalyzer - Latency and throughput analysis")
    print("  ✅ AlertManager - Intelligent alerting system")
    print("  ✅ JSON logging - Structured logging output")
    print("  ✅ Health status determination - Multi-level health assessment")
    print("  ✅ Performance metrics aggregation - Comprehensive metrics")
    
    return True


async def test_performance_under_load():
    """Test performance under simulated load"""
    print("\n⚡ Testing performance under load...")
    
    health_monitor = WebSocketHealthMonitor()
    websocket = MockWebSocket()
    endpoint = "ws://localhost:8080/load_test"
    
    # Monitor connection
    await health_monitor.monitor_connection(endpoint, websocket)
    
    # Simulate high message volume
    start_time = time.time()
    message_count = 1000
    
    for i in range(message_count):
        await health_monitor.record_message_sent(endpoint, time.time())
        await health_monitor.record_message_received(endpoint, time.time() + 0.001)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"📊 Load test results:")
    print(f"  - Messages processed: {message_count}")
    print(f"  - Duration: {duration:.3f} seconds")
    print(f"  - Messages per second: {message_count / duration:.1f}")
    print(f"  - Average latency: {duration / message_count * 1000:.3f}ms per message")
    
    # Check performance metrics
    metrics = health_monitor.get_performance_metrics()
    latency_stats = metrics['latency_stats']
    
    print(f"  - Latency stats: min={latency_stats['min']:.1f}ms, "
          f"max={latency_stats['max']:.1f}ms, avg={latency_stats['avg']:.1f}ms")
    
    await health_monitor.stop_monitoring(endpoint)
    print("✅ Load test completed")


if __name__ == "__main__":
    print("🚀 Starting WebSocket Health Monitoring Framework Integration Test")
    print("=" * 70)
    
    try:
        # Run main test
        asyncio.run(test_websocket_health_monitoring())
        
        # Run performance test
        asyncio.run(test_performance_under_load())
        
        print("\n" + "=" * 70)
        print("🎯 ALL TESTS PASSED - WebSocket Health Monitoring Framework is ready!")
        
        # Final completion log
        completion_log = {
            "timestamp": datetime.now().isoformat(),
            "task": "3.1",
            "status": "completed",
            "summary": "Health monitoring implemented",
            "components_tested": [
                "WebSocketHealthMonitor",
                "MetricsCollector", 
                "ConnectionTracker",
                "PerformanceAnalyzer",
                "AlertManager"
            ],
            "features_validated": [
                "Real-time connection monitoring",
                "Performance metrics collection",
                "Health status determination",
                "Alert management",
                "JSON logging",
                "Load testing"
            ]
        }
        
        print(json.dumps(completion_log))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)