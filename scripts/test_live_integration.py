#!/usr/bin/env python3
"""
Test Live Integration - Observatory + Engagement System
=======================================================

Tests the integration between the Observatory server and the engagement system
with live data injection and WebSocket broadcasting.
"""

import asyncio
import sys
import os
import random
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.beast_mode.observatory.models import ObservatoryConfig
from src.beast_mode.observatory.engagement.integration.server_integration import (
    ObservatoryEngagementIntegration,
    inject_observatory_metrics,
    inject_observatory_health,
    inject_observatory_costs
)


async def simulate_observatory_data_flow(integration: ObservatoryEngagementIntegration):
    """Simulate live Observatory data flowing into the engagement system."""
    print("🌊 Starting Observatory data flow simulation...")
    
    for minute in range(20):  # Simulate 20 minutes of data
        timestamp = datetime.now()
        
        # Simulate metrics data
        metrics_data = {
            "cpu_usage": 20 + minute * 2 + random.gauss(0, 5),
            "memory_usage": 40 + minute * 1.5 + random.gauss(0, 8),
            "response_time": 200 + random.gauss(0, 30),
            "active_connections": 50 + random.randint(-10, 20),
            "error_rate": max(0, 0.5 + random.gauss(0, 0.3))
        }
        
        # Add some drama at specific points
        if minute == 8:  # Crisis at minute 8
            metrics_data["response_time"] *= 3.5
            metrics_data["error_rate"] *= 5
            print(f"💥 CRISIS INJECTED at minute {minute}!")
        elif minute == 12:  # Recovery starts
            metrics_data["response_time"] *= 0.7
            metrics_data["error_rate"] *= 0.3
            print(f"🦸‍♂️ RECOVERY INITIATED at minute {minute}!")
        
        await inject_observatory_metrics(integration, metrics_data)
        
        # Simulate health data
        health_score = max(0.1, min(1.0, 0.8 + random.gauss(0, 0.1)))
        if minute == 8:  # Health drops during crisis
            health_score = 0.3
        elif minute >= 12:  # Health recovers
            health_score = min(1.0, 0.6 + (minute - 12) * 0.08)
        
        health_data = {
            "health_score": health_score,
            "status": "healthy" if health_score > 0.7 else "degraded" if health_score > 0.4 else "unhealthy",
            "uptime_seconds": minute * 60,
            "last_check": timestamp.isoformat()
        }
        
        await inject_observatory_health(integration, health_data)
        
        # Simulate cost data (every few minutes)
        if minute % 3 == 0:
            cost_data = {
                "total_cost": random.uniform(0.01, 0.15),
                "cost_per_token": random.uniform(0.0001, 0.001),
                "tokens_used": random.randint(100, 1500),
                "provider": random.choice(["openai", "anthropic", "local"]),
                "model": random.choice(["gpt-4", "claude-3", "llama-2"])
            }
            
            await inject_observatory_costs(integration, cost_data)
        
        print(f"📊 Minute {minute:2d}: CPU={metrics_data['cpu_usage']:.1f}%, "
              f"Response={metrics_data['response_time']:.0f}ms, "
              f"Health={health_score:.2f}")
        
        await asyncio.sleep(2)  # 2 seconds per "minute" for demo speed
    
    print("✅ Data flow simulation complete!")


async def monitor_insights(integration: ObservatoryEngagementIntegration):
    """Monitor and display insights as they're generated."""
    print("👁️ Starting insight monitoring...")
    
    last_pattern_count = 0
    
    while True:
        try:
            insights = await integration.data_bridge.get_recent_insights()
            
            current_pattern_count = len(insights.get("patterns", []))
            
            if current_pattern_count != last_pattern_count:
                print(f"\n🔍 NEW INSIGHTS DETECTED ({current_pattern_count} patterns):")
                print(f"   📖 Story: {insights.get('summary', 'No summary')}")
                
                if insights.get("story_arc"):
                    print(f"   🎬 Arc: {insights['story_arc'][:100]}...")
                
                drama_level = insights.get("drama_level", "PEACEFUL_TIMES")
                drama_emoji = {
                    "EPIC_BATTLE": "⚔️",
                    "CRISIS_MODE": "🚨", 
                    "RISING_ACTION": "📈",
                    "PLOT_THICKENS": "🎭",
                    "PEACEFUL_TIMES": "✨"
                }.get(drama_level, "📊")
                
                print(f"   {drama_emoji} Drama Level: {drama_level}")
                
                # Show top 3 patterns
                for i, pattern in enumerate(insights.get("patterns", [])[:3], 1):
                    print(f"   {i}. {pattern['narrative'][:80]}...")
                
                last_pattern_count = current_pattern_count
            
            await asyncio.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            print(f"Error monitoring insights: {e}")
            await asyncio.sleep(10)


async def test_live_integration():
    """Test the complete live integration."""
    print("🎯 Testing Live Observatory + Engagement Integration")
    print("=" * 60)
    
    # Create mock config
    config = ObservatoryConfig()
    
    # Initialize integration
    integration = ObservatoryEngagementIntegration(config)
    
    print("🚀 Initializing engagement integration...")
    success = await integration.initialize()
    
    if not success:
        print("❌ Failed to initialize integration")
        return False
    
    print("✅ Integration initialized successfully")
    
    # Start integration
    print("🌟 Starting engagement integration...")
    success = await integration.start_integration()
    
    if not success:
        print("❌ Failed to start integration")
        return False
    
    print("✅ Integration started successfully")
    
    # Start monitoring task
    monitor_task = asyncio.create_task(monitor_insights(integration))
    
    try:
        # Run data simulation
        await simulate_observatory_data_flow(integration)
        
        # Let monitoring run a bit longer to catch final insights
        print("\n⏳ Waiting for final insights...")
        await asyncio.sleep(10)
        
        # Get final status
        status = await integration._get_system_status()
        
        print(f"\n📊 FINAL SYSTEM STATUS:")
        print(f"   Integration Running: {status['integration_running']}")
        print(f"   Insights Broadcasted: {status['insights_broadcasted']}")
        print(f"   Active WebSockets: {status['websockets']['active_connections']}")
        print(f"   Storyteller Status: {status['storyteller']['status']}")
        print(f"   Data Bridge Running: {status['data_bridge']['running']}")
        
        # Get final insights
        final_insights = await integration.data_bridge.get_recent_insights()
        
        print(f"\n🎬 FINAL STORY:")
        print(f"   {final_insights.get('summary', 'No final story')}")
        
        if final_insights.get("story_arc"):
            print(f"\n📚 COMPLETE STORY ARC:")
            print(f"   {final_insights['story_arc']}")
        
        print(f"\n🏆 SUCCESS! Generated {len(final_insights.get('patterns', []))} dramatic stories!")
        
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        return False
        
    finally:
        # Clean up
        monitor_task.cancel()
        await integration.stop_integration()
        print("🛑 Integration stopped gracefully")


if __name__ == "__main__":
    try:
        print("🎬 Live Observatory + Engagement Integration Test")
        print("This simulates real Observatory data flowing into the engagement system")
        print("Watch for dramatic stories as the data unfolds!")
        print()
        
        result = asyncio.run(test_live_integration())
        
        if result:
            print("\n🎉 Live integration test completed successfully!")
        else:
            print("\n❌ Live integration test failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)