#!/usr/bin/env python3
"""
Observatory Engagement Integration Script
========================================

Demonstrates how to integrate the Data Storyteller and engagement features
with the existing Observatory server for live data discovery.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.beast_mode.observatory.engagement.integration.server_integration import (
    ObservatoryEngagementIntegration,
    add_engagement_websocket_to_server,
    inject_observatory_metrics,
    inject_observatory_health,
    inject_observatory_costs
)
from src.beast_mode.observatory.models import ObservatoryConfig
from src.beast_mode.observatory.config import load_observatory_config


async def demo_integration():
    """Demonstrate the Observatory engagement integration."""
    print("🎯 Observatory Engagement Integration Demo")
    print("=" * 50)
    
    try:
        # Load Observatory configuration
        print("📋 Loading Observatory configuration...")
        config = load_observatory_config()
        
        # Create engagement integration
        print("🚀 Creating engagement integration...")
        integration = ObservatoryEngagementIntegration(config)
        
        # Initialize integration
        print("⚙️ Initializing integration...")
        success = await integration.initialize()
        if not success:
            print("❌ Failed to initialize integration")
            return
        
        # Start integration
        print("🔄 Starting integration...")
        success = await integration.start_integration()
        if not success:
            print("❌ Failed to start integration")
            return
        
        print("✅ Integration started successfully!")
        
        # Simulate Observatory data injection
        print("\n📊 Simulating Observatory data injection...")
        
        # Inject sample metrics
        sample_metrics = {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "response_time": 234.5,
            "error_rate": 0.8,
            "throughput": 1250.0
        }
        await inject_observatory_metrics(integration, sample_metrics)
        print(f"✅ Injected metrics: {list(sample_metrics.keys())}")
        
        # Inject sample health data
        sample_health = {
            "status": "healthy",
            "health_score": 0.92,
            "uptime_seconds": 86400,
            "last_check": datetime.now().isoformat()
        }
        await inject_observatory_health(integration, sample_health)
        print(f"✅ Injected health data: score={sample_health['health_score']}")
        
        # Inject sample cost data
        sample_costs = {
            "total_cost": 12.45,
            "cost_per_token": 0.0001,
            "tokens_used": 124500,
            "provider": "openai",
            "model": "gpt-4"
        }
        await inject_observatory_costs(integration, sample_costs)
        print(f"✅ Injected cost data: ${sample_costs['total_cost']}")
        
        # Wait for data processing
        print("\n⏳ Waiting for data processing and pattern discovery...")
        await asyncio.sleep(5)
        
        # Get system status
        print("\n📈 Getting system status...")
        status = await integration._get_system_status()
        
        print(f"Integration Status:")
        print(f"  Running: {status['integration_running']}")
        print(f"  Insights Broadcasted: {status['insights_broadcasted']}")
        print(f"  Data Bridge Running: {status['data_bridge']['running']}")
        print(f"  Metrics Processed: {status['data_bridge']['metrics_processed']}")
        print(f"  Storyteller Status: {status['storyteller']['status']}")
        print(f"  Active Patterns: {status['storyteller']['active_patterns']}")
        
        # Get recent insights
        print("\n🔍 Getting recent insights...")
        insights = await integration.data_bridge.get_recent_insights()
        
        print(f"Insights Summary: {insights['summary']}")
        print(f"Patterns Discovered: {len(insights['patterns'])}")
        
        for i, pattern in enumerate(insights['patterns'][:3], 1):  # Show first 3 patterns
            print(f"  {i}. {pattern['narrative']}")
            print(f"     Interest: {pattern['interest_level']}, Confidence: {pattern['confidence']:.1%}")
        
        # Demonstrate WebSocket capabilities
        print(f"\n🔌 WebSocket Status:")
        print(f"  Active Connections: {len(integration.websocket_manager.active_connections)}")
        print(f"  Ready for real-time broadcasting: ✅")
        
        # Show how to add to FastAPI server
        print(f"\n🌐 Integration Instructions:")
        print(f"  To add to Observatory server:")
        print(f"  1. Import: from scripts.integrate_engagement_with_observatory import ObservatoryEngagementIntegration")
        print(f"  2. Create: integration = ObservatoryEngagementIntegration(config)")
        print(f"  3. Initialize: await integration.initialize()")
        print(f"  4. Start: await integration.start_integration()")
        print(f"  5. Add WebSocket: add_engagement_websocket_to_server(app, integration)")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"The Data Storyteller is now discovering patterns in Observatory data!")
        
        # Keep running for a bit to show continuous operation
        print(f"\n⏰ Running for 30 more seconds to show continuous operation...")
        for i in range(6):
            await asyncio.sleep(5)
            
            # Inject more data to show continuous discovery
            import random
            new_metrics = {
                "cpu_usage": 45.2 + random.gauss(0, 5),
                "response_time": 234.5 + random.gauss(0, 50),
                "error_rate": max(0, 0.8 + random.gauss(0, 0.3))
            }
            await inject_observatory_metrics(integration, new_metrics)
            
            # Check for new patterns
            current_insights = await integration.data_bridge.get_recent_insights()
            pattern_count = len(current_insights['patterns'])
            print(f"  ⏱️ {(i+1)*5}s: {pattern_count} patterns discovered")
        
        # Stop integration
        print(f"\n🛑 Stopping integration...")
        await integration.stop_integration()
        print(f"✅ Integration stopped gracefully")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


async def test_websocket_simulation():
    """Simulate WebSocket client interactions."""
    print("\n🔌 WebSocket Simulation")
    print("-" * 30)
    
    # This would normally be done by a real WebSocket client
    print("📱 Simulating WebSocket client messages:")
    print("  - get_insights: Request current insights")
    print("  - get_status: Request system status") 
    print("  - add_data_point: Add custom data")
    print("  - ping: Connection health check")
    
    print("📡 Simulating server broadcasts:")
    print("  - insights_update: New patterns discovered")
    print("  - status_update: System status changes")
    print("  - error: Error notifications")


if __name__ == "__main__":
    print("🎯 Observatory Engagement Integration")
    print("Choose demo mode:")
    print("1. Full Integration Demo (recommended)")
    print("2. WebSocket Simulation")
    
    try:
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "2":
            asyncio.run(test_websocket_simulation())
        else:
            asyncio.run(demo_integration())
            
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)