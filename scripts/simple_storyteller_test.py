#!/usr/bin/env python3
"""
Simple Data Storyteller Test
============================

A minimal test of the Data Storyteller Engine without complex dependencies.
"""

import asyncio
import sys
import os
import random
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import only what we need
try:
    from src.beast_mode.observatory.engagement.intelligence.data_storyteller import (
        DataStorytellerEngine, DataPoint, PatternType, InterestLevel
    )
    print("✅ Successfully imported Data Storyteller components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


async def simple_test():
    """Run a simple test of the Data Storyteller."""
    print("🎯 Simple Data Storyteller Test")
    print("=" * 40)
    
    # Create storyteller
    storyteller = DataStorytellerEngine()
    
    print("📊 Initializing storyteller...")
    success = await storyteller.initialize()
    
    if not success:
        print("❌ Failed to initialize storyteller")
        return
    
    print("✅ Storyteller initialized successfully")
    
    # Generate some test data
    print("\n📈 Generating test data...")
    base_time = datetime.now() - timedelta(minutes=30)
    
    # Create trending data
    for i in range(30):
        timestamp = base_time + timedelta(minutes=i)
        
        # CPU with upward trend
        cpu_value = 20 + (i * 1.5) + random.gauss(0, 3)
        cpu_point = DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, cpu_value)),
            metric_name="cpu_usage",
            source="test",
            quality_score=0.95
        )
        await storyteller.add_data_point(cpu_point)
        
        # Response time with anomaly
        response_base = 200 + random.gauss(0, 20)
        if i == 20:  # Add spike
            response_base *= 3
        
        response_point = DataPoint(
            timestamp=timestamp,
            value=max(0, response_base),
            metric_name="response_time", 
            source="test",
            quality_score=0.9
        )
        await storyteller.add_data_point(response_point)
    
    print(f"✅ Generated 60 data points across 2 metrics")
    
    # Wait for analysis
    print("\n⏳ Running pattern analysis...")
    await asyncio.sleep(2)
    
    # Discover patterns
    patterns = await storyteller.discover_patterns()
    
    print(f"\n🔍 Found {len(patterns)} patterns:")
    for i, pattern in enumerate(patterns, 1):
        print(f"   {i}. {pattern.narrative}")
        print(f"      Interest: {pattern.interest_level.value}")
        print(f"      Confidence: {pattern.confidence:.1%}")
    
    # Get insights
    insights = await storyteller.get_current_insights()
    print(f"\n📊 Summary: {insights['summary']}")
    
    # Check health
    health = storyteller.get_health_status()
    print(f"\n🏥 Health: {health['status']} - {health['active_patterns']} active patterns")
    
    print("\n✅ Test completed successfully!")
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(simple_test())
        if result:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)