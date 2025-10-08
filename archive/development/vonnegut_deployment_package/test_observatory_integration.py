#!/usr/bin/env python3
"""
Test Observatory Integration - Verify Data Storyteller Integration
=================================================================

Tests the integration between the Data Storyteller and Observatory
to ensure live data flows correctly and insights are generated.
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.beast_mode.observatory.engagement.intelligence.data_storyteller import (
        DataStorytellerEngine, DataPoint
    )
    from src.beast_mode.observatory.engagement.integration.observatory_data_bridge import (
        ObservatoryDataBridge
    )
    from src.beast_mode.observatory.engagement.integration.server_integration import (
        ObservatoryEngagementIntegration
    )
    from src.beast_mode.observatory.models import ObservatoryConfig
    from src.beast_mode.observatory.config import load_observatory_config
    
    print("✅ Successfully imported Observatory integration components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


async def test_data_bridge():
    """Test the Observatory Data Bridge functionality."""
    print("\n🌉 Testing Observatory Data Bridge")
    print("=" * 50)
    
    try:
        # Load Observatory config
        config = load_observatory_config()
        
        # Create storyteller and data bridge
        storyteller = DataStorytellerEngine()
        await storyteller.initialize()
        
        data_bridge = ObservatoryDataBridge(config, storyteller)
        await data_bridge.initialize()
        
        print("✅ Data bridge initialized successfully")
        
        # Simulate some Observatory data
        print("\n📊 Simulating Observatory data...")
        
        # Simulate metrics data
        base_time = datetime.now()
        for i in range(10):
            timestamp = base_time + timedelta(seconds=i * 5)
            
            # CPU usage metric
            cpu_point = DataPoint(
                timestamp=timestamp,
                value=30 + (i * 2) + (i % 3),  # Trending up with some variation
                metric_name="cpu_usage",
                source="observatory_metrics",
                quality_score=0.95
            )
            await storyteller.add_data_point(cpu_point)
            
            # Memory usage metric
            memory_point = DataPoint(
                timestamp=timestamp,
                value=50 + (i * 1.5) + (i % 2),
                metric_name="memory_usage", 
                source="observatory_metrics",
                quality_score=0.93
            )
            await storyteller.add_data_point(memory_point)
            
            # Response time with anomaly
            response_base = 200 + (i * 5)
            if i == 7:  # Add anomaly
                response_base *= 2.5
            
            response_point = DataPoint(
                timestamp=timestamp,
                value=response_base,
                metric_name="response_time",
                source="observatory_metrics",
                quality_score=0.9
            )
            await storyteller.add_data_point(response_point)
        
        print(f"✅ Added 30 data points across 3 metrics")
        
        # Wait for analysis
        print("\n⏳ Waiting for pattern analysis...")
        await asyncio.sleep(3)
        
        # Get insights from bridge
        insights = await data_bridge.get_recent_insights()
        
        print(f"\n🔍 Bridge Insights:")
        print(f"   Summary: {insights['summary']}")
        print(f"   Patterns found: {len(insights.get('patterns', []))}")
        
        for i, pattern in enumerate(insights.get('patterns', [])[:5], 1):
            print(f"   {i}. {pattern.get('narrative', 'No narrative')}")
            print(f"      Interest: {pattern.get('interest_level', 'unknown')}")
        
        # Get bridge status
        status = await data_bridge.get_bridge_status()
        print(f"\n📊 Bridge Status:")
        print(f"   Running: {status['running']}")
        print(f"   Metrics processed: {status['metrics_processed']}")
        print(f"   Storyteller active: {status['storyteller_active']}")
        
        await data_bridge.stop_bridge()
        print("\n✅ Data bridge test completed successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ Data bridge test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_server_integration():
    """Test the Observatory Server Integration."""
    print("\n🖥️ Testing Observatory Server Integration")
    print("=" * 50)
    
    try:
        # Load Observatory config
        config = load_observatory_config()
        
        # Create server integration
        integration = ObservatoryEngagementIntegration(config)
        await integration.initialize()
        await integration.start_integration()
        
        print("✅ Server integration started successfully")
        
        # Wait for some data processing
        await asyncio.sleep(5)
        
        # Get integration status
        status = await integration.get_integration_status()
        print(f"\n📊 Integration Status:")
        print(f"   Running: {status['integration_running']}")
        print(f"   Uptime: {status['uptime_seconds']:.1f} seconds")
        print(f"   WebSocket connections: {status['websocket_connections']['active_connections']}")
        print(f"   Data bridge running: {status['data_bridge']['running']}")
        
        # Get live insights
        insights_response = await integration.get_live_insights_api()
        print(f"\n🔍 Live Insights API:")
        print(f"   Status: {insights_response['status']}")
        if insights_response['status'] == 'success':
            insights = insights_response['insights']
            print(f"   Summary: {insights.get('summary', 'No summary')}")
            print(f"   Patterns: {len(insights.get('patterns', []))}")
        
        await integration.stop_integration()
        print("\n✅ Server integration test completed successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ Server integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_websocket_simulation():
    """Simulate WebSocket interactions."""
    print("\n🔌 Testing WebSocket Simulation")
    print("=" * 50)
    
    try:
        from src.beast_mode.observatory.engagement.integration.server_integration import (
            EngagementWebSocketManager
        )
        
        # Create WebSocket manager
        ws_manager = EngagementWebSocketManager()
        
        # Simulate connection stats
        print("📊 WebSocket Manager initialized")
        stats = ws_manager.get_connection_stats()
        print(f"   Active connections: {stats['active_connections']}")
        print(f"   Total messages sent: {stats['total_messages_sent']}")
        
        # Simulate broadcasting
        test_message = {
            "type": "test_broadcast",
            "data": {"message": "Hello from integration test!"},
            "timestamp": datetime.now().isoformat()
        }
        
        await ws_manager.send_to_all(test_message)
        print("✅ WebSocket broadcast simulation completed")
        
        return True
        
    except Exception as e:
        print(f"❌ WebSocket simulation failed: {e}")
        return False


async def run_integration_tests():
    """Run all integration tests."""
    print("🎯 Observatory Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Data Bridge", test_data_bridge),
        ("Server Integration", test_server_integration),
        ("WebSocket Simulation", test_websocket_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = await test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"💥 {test_name} test ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests PASSED!")
        return True
    else:
        print("⚠️ Some integration tests FAILED")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(run_integration_tests())
        if success:
            print("\n🚀 Observatory integration is ready!")
            sys.exit(0)
        else:
            print("\n❌ Observatory integration has issues")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)