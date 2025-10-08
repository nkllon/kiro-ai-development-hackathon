#!/usr/bin/env python3
"""
Create Interesting Patterns - Dramatic Data Scenarios
=====================================================

Creates interesting and varied data patterns that will give the Data Storyteller
compelling stories to discover and tell.
"""

import asyncio
import sys
import os
import random
import math
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.beast_mode.observatory.engagement.intelligence.data_storyteller import (
    DataStorytellerEngine, DataPoint
)


async def create_correlation_drama(storyteller: DataStorytellerEngine):
    """Create a dramatic correlation story - when CPU and memory become best friends."""
    print("🤝 Creating Correlation Drama: The CPU-Memory Love Story")
    
    base_time = datetime.now() - timedelta(minutes=30)
    
    # Phase 1: Independent behavior (first 10 minutes)
    for i in range(10):
        timestamp = base_time + timedelta(minutes=i)
        
        # CPU doing its own thing
        cpu_value = 30 + random.gauss(0, 8)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, cpu_value)),
            metric_name="cpu_usage",
            source="correlation_drama",
            quality_score=0.95
        ))
        
        # Memory doing its own thing (independent)
        memory_value = 45 + random.gauss(0, 10)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, memory_value)),
            metric_name="memory_usage",
            source="correlation_drama",
            quality_score=0.95
        ))
    
    print("   📊 Phase 1: CPU and Memory living separate lives...")
    
    # Phase 2: They start to correlate (minutes 10-20)
    for i in range(10, 20):
        timestamp = base_time + timedelta(minutes=i)
        
        # CPU starts trending up
        cpu_base = 30 + (i - 10) * 3
        cpu_value = cpu_base + random.gauss(0, 5)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, cpu_value)),
            metric_name="cpu_usage",
            source="correlation_drama",
            quality_score=0.95
        ))
        
        # Memory starts following CPU (strong positive correlation)
        memory_correlated = 45 + (cpu_value - 30) * 0.8 + random.gauss(0, 3)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, memory_correlated)),
            metric_name="memory_usage",
            source="correlation_drama",
            quality_score=0.95
        ))
    
    print("   💕 Phase 2: CPU and Memory discover they're soulmates!")
    
    # Phase 3: Perfect synchronization (minutes 20-30)
    for i in range(20, 30):
        timestamp = base_time + timedelta(minutes=i)
        
        # CPU with some variation
        cpu_base = 60 + math.sin((i - 20) * 0.5) * 15
        cpu_value = cpu_base + random.gauss(0, 3)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, cpu_value)),
            metric_name="cpu_usage",
            source="correlation_drama",
            quality_score=0.95
        ))
        
        # Memory perfectly synchronized
        memory_synchronized = 45 + (cpu_value - 30) * 0.9 + random.gauss(0, 2)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, memory_synchronized)),
            metric_name="memory_usage",
            source="correlation_drama",
            quality_score=0.95
        ))
    
    print("   🎭 Phase 3: Perfect synchronization - they dance together!")


async def create_anomaly_adventure(storyteller: DataStorytellerEngine):
    """Create an anomaly adventure - the response time roller coaster."""
    print("🎢 Creating Anomaly Adventure: The Response Time Roller Coaster")
    
    base_time = datetime.now() - timedelta(minutes=25)
    
    # Normal baseline
    for i in range(15):
        timestamp = base_time + timedelta(minutes=i)
        
        response_value = 180 + random.gauss(0, 15)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, response_value),
            metric_name="response_time",
            source="anomaly_adventure",
            quality_score=0.9
        ))
    
    print("   🎵 Baseline: Response time bebopping along normally...")
    
    # The anomaly adventure begins!
    anomaly_events = [
        (15, 4.5, "💥 MASSIVE SPIKE - Something exploded!"),
        (16, 0.3, "🕳️ DRAMATIC DROP - System overcorrected!"),
        (17, 2.8, "⚡ ANOTHER SPIKE - The plot thickens!"),
        (18, 0.6, "📉 RECOVERY DIP - Heroes fighting back!"),
        (19, 1.2, "🎯 STABILIZING - Victory in sight!"),
    ]
    
    for minute, multiplier, description in anomaly_events:
        timestamp = base_time + timedelta(minutes=minute)
        
        response_value = 180 * multiplier + random.gauss(0, 10)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, response_value),
            metric_name="response_time",
            source="anomaly_adventure",
            quality_score=0.9
        ))
        
        print(f"   {description}")
    
    # Final stabilization
    for i in range(20, 25):
        timestamp = base_time + timedelta(minutes=i)
        
        response_value = 190 + random.gauss(0, 12)  # Slightly elevated but stable
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, response_value),
            metric_name="response_time",
            source="anomaly_adventure",
            quality_score=0.9
        ))
    
    print("   ✅ Finale: Response time finds its new normal!")


async def create_trend_trilogy(storyteller: DataStorytellerEngine):
    """Create a trend trilogy - the three-act throughput drama."""
    print("📈 Creating Trend Trilogy: The Three-Act Throughput Drama")
    
    base_time = datetime.now() - timedelta(minutes=30)
    
    # Act 1: The Rise (minutes 0-10)
    print("   🎬 Act 1: The Rise - Throughput climbs to glory!")
    for i in range(10):
        timestamp = base_time + timedelta(minutes=i)
        
        # Steady upward trend
        throughput_value = 500 + i * 50 + random.gauss(0, 20)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, throughput_value),
            metric_name="throughput",
            source="trend_trilogy",
            quality_score=0.92
        ))
    
    # Act 2: The Fall (minutes 10-20)
    print("   🎭 Act 2: The Fall - Hubris leads to downfall!")
    for i in range(10, 20):
        timestamp = base_time + timedelta(minutes=i)
        
        # Dramatic decline
        throughput_value = 1000 - (i - 10) * 80 + random.gauss(0, 25)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, throughput_value),
            metric_name="throughput",
            source="trend_trilogy",
            quality_score=0.92
        ))
    
    # Act 3: The Redemption (minutes 20-30)
    print("   🏆 Act 3: The Redemption - Heroes save the day!")
    for i in range(20, 30):
        timestamp = base_time + timedelta(minutes=i)
        
        # Gradual recovery with some struggle
        recovery_base = 200 + (i - 20) * 35
        throughput_value = recovery_base + random.gauss(0, 30)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, throughput_value),
            metric_name="throughput",
            source="trend_trilogy",
            quality_score=0.92
        ))


async def create_inverse_relationship_drama(storyteller: DataStorytellerEngine):
    """Create an inverse relationship drama - when error rate and success rate become enemies."""
    print("⚔️ Creating Inverse Relationship Drama: The Error vs Success Battle")
    
    base_time = datetime.now() - timedelta(minutes=20)
    
    for i in range(20):
        timestamp = base_time + timedelta(minutes=i)
        
        # Create a battle scenario
        battle_intensity = math.sin(i * 0.3) * 0.5 + 0.5  # 0 to 1
        
        # Error rate rises during battles
        error_base = 0.5 + battle_intensity * 3
        error_value = error_base + random.gauss(0, 0.3)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, error_value),
            metric_name="error_rate",
            source="inverse_drama",
            quality_score=0.98
        ))
        
        # Success rate inversely correlated (when errors go up, success goes down)
        success_base = 98 - battle_intensity * 15
        success_value = success_base + random.gauss(0, 1)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, success_value)),
            metric_name="success_rate",
            source="inverse_drama",
            quality_score=0.98
        ))
        
        if i % 5 == 0:
            battle_status = "🔥 INTENSE BATTLE" if battle_intensity > 0.7 else "⚖️ Balanced Fight" if battle_intensity > 0.3 else "✨ Peaceful Times"
            print(f"   Minute {i:2d}: {battle_status} - Errors: {error_value:.1f}%, Success: {success_value:.1f}%")


async def create_cyclical_mystery(storyteller: DataStorytellerEngine):
    """Create a cyclical mystery - the mysterious daily pattern."""
    print("🔄 Creating Cyclical Mystery: The Daily Pattern Enigma")
    
    base_time = datetime.now() - timedelta(minutes=24)  # 24 "hours" in minutes
    
    for i in range(24):
        timestamp = base_time + timedelta(minutes=i)
        
        # Create a daily cycle (like user activity)
        hour_of_day = i
        
        # Simulate daily user activity pattern
        if 6 <= hour_of_day <= 9:  # Morning rush
            activity_base = 70 + (hour_of_day - 6) * 10
        elif 9 <= hour_of_day <= 17:  # Work hours
            activity_base = 100 + math.sin((hour_of_day - 9) * 0.5) * 20
        elif 17 <= hour_of_day <= 21:  # Evening peak
            activity_base = 120 - (hour_of_day - 17) * 5
        else:  # Night time
            activity_base = 20 + random.gauss(0, 5)
        
        activity_value = activity_base + random.gauss(0, 8)
        await storyteller.add_data_point(DataPoint(
            timestamp=timestamp,
            value=max(0, activity_value),
            metric_name="user_activity",
            source="cyclical_mystery",
            quality_score=0.94
        ))
        
        if hour_of_day in [6, 9, 12, 17, 21, 0]:
            time_desc = {6: "🌅 Morning Rush", 9: "💼 Work Begins", 12: "🍽️ Lunch Peak", 
                        17: "🏠 Evening Rush", 21: "📺 Prime Time", 0: "🌙 Midnight Quiet"}
            print(f"   Hour {hour_of_day:2d}: {time_desc[hour_of_day]} - Activity: {activity_value:.0f}")


async def run_interesting_pattern_showcase():
    """Run the complete showcase of interesting patterns."""
    print("🎪 INTERESTING PATTERN SHOWCASE")
    print("=" * 60)
    print("Creating multiple dramatic scenarios for the Data Storyteller to discover...")
    print()
    
    storyteller = DataStorytellerEngine()
    await storyteller.initialize()
    
    # Create all the interesting patterns
    await create_correlation_drama(storyteller)
    print()
    
    await create_anomaly_adventure(storyteller)
    print()
    
    await create_trend_trilogy(storyteller)
    print()
    
    await create_inverse_relationship_drama(storyteller)
    print()
    
    await create_cyclical_mystery(storyteller)
    print()
    
    print("⏳ Letting the Data Storyteller analyze all these interesting patterns...")
    await asyncio.sleep(5)  # Give time for analysis
    
    # Discover all the patterns
    patterns = await storyteller.discover_patterns()
    correlations = await storyteller.analyze_correlations()
    
    # Get the complete story
    insights = await storyteller.get_current_insights()
    
    print("\n" + "=" * 60)
    print("🎬 THE COMPLETE DRAMATIC SAGA")
    print("=" * 60)
    
    print(f"\n📊 DRAMA LEVEL: {insights.get('drama_level', 'UNKNOWN')}")
    
    print(f"\n📖 EXECUTIVE SUMMARY:")
    print(f"   {insights['summary']}")
    
    if insights.get('story_arc'):
        print(f"\n📚 COMPLETE STORY ARC:")
        print(f"   {insights['story_arc']}")
    
    print(f"\n🎭 DISCOVERED STORIES ({len(patterns)} patterns):")
    for i, pattern in enumerate(patterns[:8], 1):  # Show top 8
        print(f"   {i}. {pattern.narrative}")
    
    print(f"\n🔗 RELATIONSHIP DISCOVERIES ({len(correlations)} correlations):")
    for i, corr in enumerate(correlations[:5], 1):  # Show top 5
        corr_type = "💕 Love Story" if corr.correlation_coefficient > 0.8 else "🤝 Partnership" if corr.correlation_coefficient > 0.5 else "⚔️ Rivalry" if corr.correlation_coefficient < -0.5 else "🔄 Complex Relationship"
        print(f"   {i}. {corr_type}: {corr.metric_a} & {corr.metric_b} (r={corr.correlation_coefficient:.2f})")
    
    print(f"\n📈 ANALYSIS STATISTICS:")
    print(f"   • Total patterns discovered: {len(patterns)}")
    print(f"   • Correlations found: {len(correlations)}")
    print(f"   • Metrics analyzed: {insights['metrics_analyzed']}")
    print(f"   • Data points processed: {insights['total_data_points']}")
    
    # Pattern breakdown
    critical = len([p for p in patterns if p.interest_level.value == 'critical'])
    high = len([p for p in patterns if p.interest_level.value == 'high'])
    medium = len([p for p in patterns if p.interest_level.value == 'medium'])
    
    print(f"\n🎯 DRAMA BREAKDOWN:")
    print(f"   • Epic Battles (Critical): {critical}")
    print(f"   • Major Conflicts (High): {high}")
    print(f"   • Plot Developments (Medium): {medium}")
    
    print("\n" + "=" * 60)
    print("🎉 SHOWCASE COMPLETE!")
    print("The Data Storyteller has discovered and narrated multiple dramatic sagas!")
    print("=" * 60)
    
    return insights


if __name__ == "__main__":
    try:
        print("🎪 Welcome to the Interesting Pattern Showcase!")
        print("We're going to create fascinating data scenarios for our storyteller...")
        print()
        
        result = asyncio.run(run_interesting_pattern_showcase())
        
        print(f"\n🏆 Showcase completed successfully!")
        print(f"Generated {len(result['patterns'])} compelling stories across multiple dramatic scenarios!")
        
    except KeyboardInterrupt:
        print("\n👋 Showcase interrupted by user")
    except Exception as e:
        print(f"\n💥 Showcase error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)