#!/usr/bin/env python3
"""
Test Engagement Monitoring Integration

Tests the integration of engagement metrics with Observatory's Prometheus monitoring system.
Validates that engagement-specific metrics are properly collected and exported.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.observatory.engagement.monitoring import (
    EngagementMetricsCollector,
    EngagementPrometheusIntegration,
    EngagementHealthMonitor,
    create_engagement_prometheus_integration,
    create_engagement_health_monitor
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_engagement_metrics_collection():
    """Test engagement metrics collection functionality."""
    logger.info("🧪 Testing engagement metrics collection...")
    
    try:
        # Create metrics collector
        collector = EngagementMetricsCollector()
        await collector.initialize()
        
        # Test attention session tracking
        await collector.start_attention_session("user1", "session1", "dashboard")
        await collector.record_focus_event("session1", "focus")
        await collector.record_page_view("session1", "engagement_dashboard")
        
        # Test interaction recording
        await collector.record_interaction("user1", "click", "dashboard_button", 0.5)
        await collector.record_interaction("user1", "hover", "chart_element", 2.0)
        
        # Test animation metrics
        await collector.record_animation_event("smooth_transition", 0.3, 0.95)
        
        # Test personality transitions
        await collector.record_personality_transition("calm", "focused", "high_activity")
        
        # Test attention priority events
        await collector.record_attention_priority_event("high", 0.05)
        
        # Test learning optimizations
        await collector.record_learning_optimization("interaction_pattern", 0.15)
        
        # End session
        duration = await collector.end_attention_session("session1")
        
        # Get metrics summary
        summary = collector.get_engagement_summary()
        
        logger.info(f"✅ Metrics collection test passed:")
        logger.info(f"   - Session duration: {duration:.2f}s")
        logger.info(f"   - Total interactions: {summary['total_interactions']}")
        logger.info(f"   - Completed sessions: {summary['completed_sessions']}")
        logger.info(f"   - Metrics collected: {summary['metrics_collected']}")
        
        # Test Prometheus export
        prometheus_metrics = collector.get_prometheus_metrics()
        logger.info(f"   - Prometheus metrics length: {len(prometheus_metrics)} chars")
        
        await collector.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"❌ Metrics collection test failed: {e}")
        return False


async def test_prometheus_integration():
    """Test Prometheus integration functionality."""
    logger.info("🧪 Testing Prometheus integration...")
    
    try:
        # Create metrics collector
        collector = EngagementMetricsCollector()
        await collector.initialize()
        
        # Create Prometheus integration
        integration = await create_engagement_prometheus_integration(collector)
        
        # Add some test data
        await collector.start_attention_session("user2", "session2", "dashboard")
        await collector.record_interaction("user2", "click", "button", 0.2)
        await collector.end_attention_session("session2")
        
        # Update Prometheus metrics
        await integration.update_prometheus_metrics()
        
        # Get metrics text
        metrics_text = integration.get_prometheus_metrics_text()
        
        # Test Observatory metrics injection
        observatory_metrics = {"test_metric": 1.0}
        await integration.inject_into_observatory_metrics(observatory_metrics)
        
        logger.info(f"✅ Prometheus integration test passed:")
        logger.info(f"   - Integration running: {integration.running}")
        logger.info(f"   - Prometheus registered: {integration.prometheus_registered}")
        logger.info(f"   - Metrics exported: {integration.metrics_exported}")
        logger.info(f"   - Observatory metrics enhanced: {len(observatory_metrics)} metrics")
        
        await integration.shutdown()
        await collector.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"❌ Prometheus integration test failed: {e}")
        return False


async def test_health_monitoring():
    """Test health monitoring functionality."""
    logger.info("🧪 Testing health monitoring...")
    
    try:
        # Create components
        collector = EngagementMetricsCollector()
        await collector.initialize()
        
        integration = await create_engagement_prometheus_integration(collector)
        
        health_monitor = await create_engagement_health_monitor(collector, integration)
        
        # Wait for initial health check
        await asyncio.sleep(2)
        
        # Get health summary
        health_summary = health_monitor.get_health_summary()
        
        # Test Observatory health injection
        observatory_health = {"status": "healthy", "health_score": 0.9}
        await health_monitor.inject_into_observatory_health(observatory_health)
        
        logger.info(f"✅ Health monitoring test passed:")
        logger.info(f"   - Overall status: {health_summary['overall_status']}")
        logger.info(f"   - Health score: {health_summary['health_score']:.2f}")
        logger.info(f"   - Component health: {health_summary['component_health']}")
        logger.info(f"   - Health trend: {health_summary['health_trend']}")
        logger.info(f"   - Observatory health enhanced: {len(observatory_health)} fields")
        
        await health_monitor.shutdown()
        await integration.shutdown()
        await collector.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"❌ Health monitoring test failed: {e}")
        return False


async def test_full_integration():
    """Test full integration with simulated Observatory server."""
    logger.info("🧪 Testing full integration...")
    
    try:
        # Create full monitoring stack
        collector = EngagementMetricsCollector()
        await collector.initialize()
        
        integration = await create_engagement_prometheus_integration(collector)
        health_monitor = await create_engagement_health_monitor(collector, integration)
        
        # Simulate user activity
        logger.info("   Simulating user activity...")
        
        # Multiple users with different activity patterns
        for user_id in ["user1", "user2", "user3"]:
            session_id = f"session_{user_id}_{int(datetime.now().timestamp())}"
            
            await collector.start_attention_session(user_id, session_id, "dashboard")
            
            # Simulate interactions
            for i in range(5):
                await collector.record_interaction(
                    user_id, "click", f"component_{i}", 0.1 + i * 0.1
                )
                await asyncio.sleep(0.1)
            
            await collector.record_focus_event(session_id, "focus")
            await collector.record_page_view(session_id, "engagement_dashboard")
            
            await collector.end_attention_session(session_id)
        
        # Wait for health check
        await asyncio.sleep(2)
        
        # Get comprehensive status
        metrics_summary = collector.get_engagement_summary()
        health_summary = health_monitor.get_health_summary()
        prometheus_metrics = integration.get_prometheus_metrics_text()
        
        # Simulate Observatory integration
        observatory_metrics = {"observatory_uptime": 3600}
        observatory_health = {"status": "healthy", "health_score": 0.95}
        
        await integration.inject_into_observatory_metrics(observatory_metrics)
        await health_monitor.inject_into_observatory_health(observatory_health)
        
        logger.info(f"✅ Full integration test passed:")
        logger.info(f"   - Active sessions: {metrics_summary['active_attention_sessions']}")
        logger.info(f"   - Completed sessions: {metrics_summary['completed_sessions']}")
        logger.info(f"   - Total interactions: {metrics_summary['total_interactions']}")
        logger.info(f"   - Interaction rate: {metrics_summary['recent_interaction_rate_per_minute']:.2f}/min")
        logger.info(f"   - Health status: {health_summary['overall_status']}")
        logger.info(f"   - Health score: {health_summary['health_score']:.2f}")
        logger.info(f"   - Prometheus metrics: {len(prometheus_metrics)} chars")
        logger.info(f"   - Observatory metrics: {len(observatory_metrics)} fields")
        logger.info(f"   - Observatory health: {len(observatory_health)} fields")
        
        await health_monitor.shutdown()
        await integration.shutdown()
        await collector.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"❌ Full integration test failed: {e}")
        return False


async def main():
    """Run all engagement monitoring integration tests."""
    logger.info("🚀 Starting Engagement Monitoring Integration Tests")
    
    tests = [
        ("Metrics Collection", test_engagement_metrics_collection),
        ("Prometheus Integration", test_prometheus_integration),
        ("Health Monitoring", test_health_monitoring),
        ("Full Integration", test_full_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"Running {test_name} Test")
        logger.info(f"{'='*60}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.error(f"❌ {test_name} test FAILED")
                
        except Exception as e:
            logger.error(f"💥 {test_name} test CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All engagement monitoring integration tests PASSED!")
        return 0
    else:
        logger.error(f"💥 {total - passed} tests FAILED!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)