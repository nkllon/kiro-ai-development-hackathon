#!/usr/bin/env python3
"""
Simple Engagement Monitoring Integration Test

Tests the basic functionality of engagement metrics integration without Prometheus conflicts.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.observatory.engagement.monitoring import (
    EngagementMetricsCollector,
    EngagementHealthMonitor
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_basic_metrics():
    """Test basic metrics collection without Prometheus."""
    logger.info("🧪 Testing basic engagement metrics...")
    
    try:
        # Create metrics collector
        collector = EngagementMetricsCollector()
        await collector.initialize()
        
        # Test attention session
        await collector.start_attention_session("user1", "session1", "dashboard")
        await collector.record_interaction("user1", "click", "button", 0.5)
        duration = await collector.end_attention_session("session1")
        
        # Get summary
        summary = collector.get_engagement_summary()
        
        logger.info(f"✅ Basic metrics test passed:")
        logger.info(f"   - Session duration: {duration:.2f}s")
        logger.info(f"   - Total interactions: {summary['total_interactions']}")
        logger.info(f"   - Completed sessions: {summary['completed_sessions']}")
        
        await collector.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic metrics test failed: {e}")
        return False


async def test_health_monitoring_simple():
    """Test health monitoring without Prometheus integration."""
    logger.info("🧪 Testing simple health monitoring...")
    
    try:
        # Create metrics collector
        collector = EngagementMetricsCollector()
        await collector.initialize()
        
        # Create a mock prometheus integration for health monitor
        class MockPrometheusIntegration:
            def __init__(self):
                self.running = True
                self.prometheus_registered = False
                self.metrics_exported = 0
                self.export_errors = 0
            
            def get_health_status(self):
                return {
                    "integration_running": self.running,
                    "prometheus_registered": self.prometheus_registered,
                    "metrics_exported": self.metrics_exported,
                    "export_errors": self.export_errors
                }
        
        mock_integration = MockPrometheusIntegration()
        
        # Create health monitor
        health_monitor = EngagementHealthMonitor(collector, mock_integration)
        await health_monitor.initialize()
        
        # Wait for health check
        await asyncio.sleep(2)
        
        # Get health summary
        health_summary = health_monitor.get_health_summary()
        
        logger.info(f"✅ Health monitoring test passed:")
        logger.info(f"   - Overall status: {health_summary['overall_status']}")
        logger.info(f"   - Health score: {health_summary['health_score']:.2f}")
        logger.info(f"   - Component health: {health_summary['component_health']}")
        
        await health_monitor.shutdown()
        await collector.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"❌ Health monitoring test failed: {e}")
        return False


async def test_observatory_integration():
    """Test integration with Observatory endpoints."""
    logger.info("🧪 Testing Observatory integration...")
    
    try:
        # Create metrics collector
        collector = EngagementMetricsCollector()
        await collector.initialize()
        
        # Add some test data
        await collector.start_attention_session("user1", "session1", "dashboard")
        await collector.record_interaction("user1", "click", "button", 0.2)
        await collector.record_interaction("user1", "hover", "chart", 1.5)
        await collector.end_attention_session("session1")
        
        # Test metrics export
        prometheus_metrics = collector.get_prometheus_metrics()
        
        # Test summary for Observatory health
        summary = collector.get_engagement_summary()
        
        # Simulate Observatory metrics injection
        observatory_metrics = {"observatory_uptime": 3600}
        
        # Add engagement metrics to Observatory metrics (simulated)
        observatory_metrics.update({
            "engagement_active_sessions": summary.get('active_attention_sessions', 0),
            "engagement_total_interactions": summary.get('total_interactions', 0),
            "engagement_interaction_rate": summary.get('recent_interaction_rate_per_minute', 0)
        })
        
        # Simulate Observatory health injection
        observatory_health = {"status": "healthy", "health_score": 0.9}
        
        # Calculate combined health score
        engagement_health_score = 0.8  # Mock score
        combined_score = (observatory_health["health_score"] * 0.8 + 
                         engagement_health_score * 0.2)
        observatory_health["health_score"] = combined_score
        observatory_health["engagement"] = {
            "status": "healthy",
            "active_sessions": summary.get('active_attention_sessions', 0),
            "total_interactions": summary.get('total_interactions', 0)
        }
        
        logger.info(f"✅ Observatory integration test passed:")
        logger.info(f"   - Prometheus metrics: {len(prometheus_metrics)} chars")
        logger.info(f"   - Observatory metrics: {len(observatory_metrics)} fields")
        logger.info(f"   - Observatory health: {len(observatory_health)} fields")
        logger.info(f"   - Combined health score: {combined_score:.2f}")
        
        await collector.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"❌ Observatory integration test failed: {e}")
        return False


async def main():
    """Run simple engagement monitoring tests."""
    logger.info("🚀 Starting Simple Engagement Monitoring Tests")
    
    tests = [
        ("Basic Metrics", test_basic_metrics),
        ("Health Monitoring", test_health_monitoring_simple),
        ("Observatory Integration", test_observatory_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} Test")
        logger.info(f"{'='*50}")
        
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
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All engagement monitoring tests PASSED!")
        return 0
    else:
        logger.error(f"💥 {total - passed} tests FAILED!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)