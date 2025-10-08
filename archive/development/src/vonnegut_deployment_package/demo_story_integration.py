#!/usr/bin/env python3
"""
Story Integration Demo - Dramatic Data Storytelling
==================================================

Demonstrates the enhanced Data Storyteller with dramatic story arcs
following the "bebopping along → something happened → response → outcome" pattern.
"""

import asyncio
import sys
import os
import random
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.beast_mode.observatory.engagement.intelligence.data_storyteller import (
    DataStorytellerEngine, DataPoint
)


async def create_dramatic_scenario():
    """Create a dramatic data scenario with multiple story arcs."""
    print("🎬 Creating Dramatic Data Scenario")
    print("=" * 50)
    
    storyteller = DataStorytellerEngine()
    await storyteller.initialize()
    
    base_time = datetime.now() - timedelta(minutes=30)
    
    print("🎵 Setting up the 'bebopping along' baseline...")
    
    # Phase 1: Everything bebopping along normally (first 15 minutes)
    for i in range(15):
        timestamp = base_time + timedelta(minutes=i)
        
        # Normal CPU usage
        cpu_value = 25 + random.gauss(0, 3)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, cpu_value)),
            metric_name="cpu_usage",
            source="demo",
            quality_score=0.95
        ))
        
        # Normal response time
        response_value = 180 + random.gauss(0, 15)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, response_value),
            metric_name="response_time",
            source="demo",
            quality_score=0.9
        ))
        
        # Normal memory usage
        memory_value = 40 + random.gauss(0, 5)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, memory_value)),
            metric_name="memory_usage",
            source="demo",
            quality_score=0.93
        ))
    
    print("✅ Baseline established - systems bebopping along peacefully")
    
    # Phase 2: Then this happened! (minutes 15-20)
    print("\n💥 THEN THIS HAPPENED...")
    
    for i in range(15, 20):
        timestamp = base_time + timedelta(minutes=i)
        
        # CPU starts spiking
        cpu_spike = 25 + (i - 15) * 15 + random.gauss(0, 8)  # Dramatic increase
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, cpu_spike)),
            metric_name="cpu_usage",
            source="demo",
            quality_score=0.95
        ))
        
        # Response time goes crazy
        if i == 17:  # Big spike at minute 17
            response_spike = 180 * 4.5  # 4.5x normal!
        else:
            response_spike = 180 + (i - 15) * 50 + random.gauss(0, 30)
        
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, response_spike),
            metric_name="response_time",
            source="demo",
            quality_score=0.9
        ))
        
        # Memory correlates with CPU
        memory_correlated = 40 + (cpu_spike * 0.8) + random.gauss(0, 5)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, memory_correlated)),
            metric_name="memory_usage",
            source="demo",
            quality_score=0.93
        ))
    
    print("🚨 Crisis initiated - multiple systems affected!")
    
    # Phase 3: We responded! (minutes 20-25)
    print("\n🦸‍♂️ OUR HEROES RESPONDED...")
    
    for i in range(20, 25):
        timestamp = base_time + timedelta(minutes=i)
        
        # CPU starts to stabilize (our response working)
        cpu_recovery = max(25, 80 - (i - 20) * 8) + random.gauss(0, 5)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, cpu_recovery)),
            metric_name="cpu_usage",
            source="demo",
            quality_score=0.95
        ))
        
        # Response time improving
        response_recovery = max(180, 800 - (i - 20) * 120) + random.gauss(0, 25)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, response_recovery),
            metric_name="response_time",
            source="demo",
            quality_score=0.9
        ))
        
        # Memory following CPU down
        memory_recovery = max(40, 80 - (i - 20) * 6) + random.gauss(0, 4)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, memory_recovery)),
            metric_name="memory_usage",
            source="demo",
            quality_score=0.93
        ))
    
    print("⚡ Response measures deployed - systems fighting back!")
    
    # Phase 4: The outcome! (minutes 25-30)
    print("\n🎯 THE OUTCOME...")
    
    for i in range(25, 30):
        timestamp = base_time + timedelta(minutes=i)
        
        # Did we save the day? (mostly yes, with some lingering issues)
        cpu_final = 30 + random.gauss(0, 4)  # Back to normal-ish
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, cpu_final)),
            metric_name="cpu_usage",
            source="demo",
            quality_score=0.95
        ))
        
        # Response time mostly recovered
        response_final = 200 + random.gauss(0, 20)  # Slightly elevated but stable
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, response_final),
            metric_name="response_time",
            source="demo",
            quality_score=0.9
        ))
        
        # Memory back to normal
        memory_final = 45 + random.gauss(0, 5)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, memory_final)),
            metric_name="memory_usage",
            source="demo",
            quality_score=0.93
        ))
    
    print("✅ Outcome achieved - let's see how the story ends!")
    
    # Wait for analysis
    await asyncio.sleep(3)
    
    # Get the dramatic story
    insights = await storyteller.get_current_insights()
    
    print("\n" + "=" * 60)
    print("🎬 THE COMPLETE STORY")
    print("=" * 60)
    
    print(f"\n📊 DRAMA LEVEL: {insights.get('drama_level', 'UNKNOWN')}")
    
    print(f"\n📖 STORY ARC:")
    print(f"   {insights.get('story_arc', 'No story arc generated')}")
    
    print(f"\n📝 SUMMARY:")
    print(f"   {insights['summary']}")
    
    print(f"\n🎭 INDIVIDUAL PATTERN STORIES:")
    for i, pattern in enumerate(insights['patterns'][:5], 1):  # Show top 5
        print(f"   {i}. {pattern['narrative']}")
    
    print(f"\n📈 ANALYSIS STATS:")
    print(f"   • Total patterns discovered: {len(insights['patterns'])}")
    print(f"   • Metrics analyzed: {insights['metrics_analyzed']}")
    print(f"   • Data points processed: {insights['total_data_points']}")
    
    # Show pattern breakdown by drama level
    critical = len([p for p in insights['patterns'] if p['interest_level'] == 'critical'])
    high = len([p for p in insights['patterns'] if p['interest_level'] == 'high'])
    medium = len([p for p in insights['patterns'] if p['interest_level'] == 'medium'])
    
    print(f"\n🎯 PATTERN BREAKDOWN:")
    print(f"   • Critical (🚨): {critical}")
    print(f"   • High (⚠️): {high}")
    print(f"   • Medium (📊): {medium}")
    
    print("\n" + "=" * 60)
    print("🎉 STORY COMPLETE - Our heroes saved the day!")
    print("=" * 60)
    
    return insights


if __name__ == "__main__":
    try:
        print("🎬 Dramatic Data Storytelling Demo")
        print("Following the pattern: bebopping along → something happened → we responded → outcome")
        print()
        
        result = asyncio.run(create_dramatic_scenario())
        
        print(f"\n🏆 Demo completed successfully!")
        print(f"Generated {len(result['patterns'])} dramatic stories!")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)