#!/usr/bin/env python3
"""
Test Data Storyteller - Demo Script
===================================

Demonstrates the Data Storyteller Engine discovering interesting patterns
in simulated Observatory data.
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


async def generate_sample_data(storyteller: DataStorytellerEngine, duration_minutes: int = 60):
    """Generate realistic sample data for testing."""
    print(f"📊 Generating {duration_minutes} minutes of sample data...")
    
    base_time = datetime.now() - timedelta(minutes=duration_minutes)
    
    for i in range(duration_minutes):
        timestamp = base_time + timedelta(minutes=i)
        
        # CPU Usage - gradual increase with noise
        cpu_base = 20 + (i * 0.8)  # Gradual increase
        cpu_noise = random.gauss(0, 5)
        cpu_value = max(0, min(100, cpu_base + cpu_noise))
        
        cpu_point = DataPoint(
            timestamp=timestamp,
            value=cpu_value,
            metric_name="cpu_usage",
            source="demo",
            quality_score=0.95
        )
        await storyteller.add_data_point(cpu_point)
        
        # Memory Usage - correlated with CPU
        memory_base = 40 + (cpu_value * 0.6) + random.gauss(0, 8)
        memory_value = max(0, min(100, memory_base))
        
        memory_point = DataPoint(
            timestamp=timestamp,
            value=memory_value,
            metric_name="memory_usage",
            source="demo",
            quality_score=0.93
        )
        await storyteller.add_data_point(memory_point)
        
        # Response Time - with occasional spikes
        response_base = 150 + random.gauss(0, 25)
        
        # Add anomalies at specific times
        if i in [15, 35, 50]:  # Spike anomalies
            response_base *= random.uniform(2.5, 4.0)
        elif i in [25]:  # Drop anomaly
            response_base *= 0.3
        
        response_point = DataPoint(
            timestamp=timestamp,
            value=max(0, response_base),
            metric_name="response_time",
            source="demo",
            quality_score=0.9
        )
        await storyteller.add_data_point(response_point)
        
        # Error Rate - mostly stable with occasional spikes
        error_base = 0.5 + random.gauss(0, 0.2)
        if i in [35, 36, 37]:  # Error spike period
            error_base += random.uniform(2.0, 5.0)
        
        error_point = DataPoint(
            timestamp=timestamp,
            value=max(0, error_base),
            metric_name="error_rate",
            source="demo",
            quality_score=0.98
        )
        await storyteller.add_data_point(error_point)
        
        # Throughput - inversely related to response time
        throughput_base = 1000 - (response_base * 2) + random.gauss(0, 50)
        throughput_point = DataPoint(
            timestamp=timestamp,
            value=max(0, throughput_base),
            metric_name="throughput",
            source="demo",
            quality_score=0.92
        )
        await storyteller.add_data_point(throughput_point)
    
    print(f"✅ Generated data for {duration_minutes} minutes across 5 metrics")


async def run_storyteller_demo():
    """Run the complete Data Storyteller demonstration."""
    print("🎯 Starting Data Storyteller Demo")
    print("=" * 50)
    
    # Initialize the storyteller
    storyteller = DataStorytellerEngine()
    await storyteller.initialize()
    
    # Generate sample data
    await generate_sample_data(storyteller, duration_minutes=60)
    
    # Wait for background analysis to complete
    print("\n⏳ Waiting for pattern analysis...")
    await asyncio.sleep(3)
    
    # Discover patterns
    print("\n🔍 Discovering patterns...")
    patterns = await storyteller.discover_patterns()
    
    # Analyze correlations
    print("🔗 Analyzing correlations...")
    correlations = await storyteller.analyze_correlations()
    
    # Get comprehensive insights
    insights = await storyteller.get_current_insights()
    
    # Display results
    print("\n" + "=" * 50)
    print("📊 DATA STORYTELLER RESULTS")
    print("=" * 50)
    
    print(f"\n📈 SUMMARY:")
    print(f"   {insights['summary']}")
    
    print(f"\n🔍 DISCOVERED PATTERNS ({len(patterns)}):")
    for i, pattern in enumerate(patterns, 1):
        interest_emoji = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '📊',
            'low': '📈'
        }.get(pattern.interest_level.value, '📊')
        
        print(f"   {i}. {interest_emoji} {pattern.narrative}")
        print(f"      Type: {pattern.pattern_type.value}")
        print(f"      Interest: {pattern.interest_level.value.upper()}")
        print(f"      Confidence: {pattern.confidence:.1%}")
        print(f"      Metrics: {', '.join(pattern.affected_metrics)}")
        print(f"      Visual: {pattern.visual_suggestion.get('animation_type', 'default')} "
              f"({pattern.visual_suggestion.get('color', '#3498db')})")
        print()
    
    print(f"🔗 CORRELATIONS FOUND ({len(correlations)}):")
    for i, corr in enumerate(correlations, 1):
        corr_strength = "Strong" if abs(corr.correlation_coefficient) > 0.8 else "Moderate"
        corr_direction = "Positive" if corr.correlation_coefficient > 0 else "Negative"
        
        print(f"   {i}. {corr_strength} {corr_direction} correlation:")
        print(f"      {corr.metric_a} ↔ {corr.metric_b}")
        print(f"      Coefficient: {corr.correlation_coefficient:.3f}")
        print(f"      Confidence: {corr.confidence:.1%}")
        if corr.lag_seconds > 0:
            print(f"      Lag: {corr.lag_seconds // 60} minutes")
        print()
    
    print(f"📊 ANALYSIS STATISTICS:")
    print(f"   Metrics analyzed: {insights['metrics_analyzed']}")
    print(f"   Total data points: {insights['total_data_points']}")
    print(f"   Analysis timestamp: {insights['analysis_timestamp']}")
    
    # Show health status
    health = storyteller.get_health_status()
    print(f"\n🏥 STORYTELLER HEALTH:")
    print(f"   Status: {health['status']}")
    print(f"   Active patterns: {health['active_patterns']}")
    print(f"   Pattern detectors: {health['pattern_detectors']}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    
    return insights


async def interactive_demo():
    """Run an interactive demo where users can see real-time pattern detection."""
    print("🎮 Interactive Data Storyteller Demo")
    print("=" * 40)
    
    storyteller = DataStorytellerEngine()
    await storyteller.initialize()
    
    print("📊 Streaming live data... (Press Ctrl+C to stop)")
    
    try:
        minute_counter = 0
        while True:
            # Generate one minute of data
            timestamp = datetime.now()
            
            # Create some interesting patterns
            if minute_counter % 10 == 0:
                # Every 10 minutes, create a spike
                spike_value = random.uniform(800, 1200)
                spike_point = DataPoint(
                    timestamp=timestamp,
                    value=spike_value,
                    metric_name="response_time",
                    source="live_demo",
                    quality_score=0.95
                )
                await storyteller.add_data_point(spike_point)
                print(f"⚡ Injected spike: response_time = {spike_value:.1f}ms")
            
            # Normal data
            normal_cpu = 30 + random.gauss(0, 10)
            cpu_point = DataPoint(
                timestamp=timestamp,
                value=max(0, min(100, normal_cpu)),
                metric_name="cpu_usage",
                source="live_demo",
                quality_score=0.95
            )
            await storyteller.add_data_point(cpu_point)
            
            # Check for new patterns every 5 minutes
            if minute_counter % 5 == 0 and minute_counter > 0:
                patterns = await storyteller.discover_patterns()
                if patterns:
                    print(f"\n🔍 New patterns discovered:")
                    for pattern in patterns[-3:]:  # Show last 3 patterns
                        print(f"   • {pattern.narrative}")
                    print()
            
            minute_counter += 1
            await asyncio.sleep(2)  # 2 seconds per "minute" for demo speed
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped by user")
        
        # Show final insights
        insights = await storyteller.get_current_insights()
        print(f"\n📊 Final Summary: {insights['summary']}")


if __name__ == "__main__":
    print("🎯 Data Storyteller Test Suite")
    print("Choose demo mode:")
    print("1. Full Demo (recommended)")
    print("2. Interactive Demo")
    
    try:
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "2":
            asyncio.run(interactive_demo())
        else:
            asyncio.run(run_storyteller_demo())
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)