#!/usr/bin/env python3
"""
Generate sample data for the Beast Mode Observatory dashboard.

This script creates realistic sample LLM API calls and metrics to populate
the dashboard charts with test data.
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from decimal import Decimal

# Add src to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.observatory.models import ObservatoryConfig
from beast_mode.observatory.llm_cost_tracker import LLMCostTracker, LLMProvider
from beast_mode.observatory.metrics_collector import MetricsCollector
from beast_mode.observatory.analytics_engine import RealTimeAnalyticsEngine


async def generate_sample_llm_calls(cost_tracker: LLMCostTracker, num_calls: int = 50):
    """Generate sample LLM API calls with realistic patterns."""
    print(f"🎯 Generating {num_calls} sample LLM API calls...")
    
    # Realistic provider/model combinations
    providers_models = [
        ("openai", "gpt-4", 0.3),
        ("openai", "gpt-3.5-turbo", 0.4),
        ("anthropic", "claude-3-opus", 0.1),
        ("anthropic", "claude-3-sonnet", 0.15),
        ("anthropic", "claude-3-haiku", 0.05),
    ]
    
    for i in range(num_calls):
        # Choose provider/model with weighted probability
        provider, model, _ = random.choices(
            providers_models, 
            weights=[weight for _, _, weight in providers_models]
        )[0]
        
        # Generate realistic token counts
        if "gpt-4" in model or "claude-3-opus" in model:
            # More expensive models tend to have longer conversations
            input_tokens = random.randint(500, 3000)
            output_tokens = random.randint(200, 1500)
        else:
            input_tokens = random.randint(100, 1500)
            output_tokens = random.randint(50, 800)
        
        # Realistic response times
        response_time = random.uniform(500, 3000)  # 0.5-3 seconds
        
        # Most calls succeed, but some fail
        success = random.random() > 0.05  # 95% success rate
        error_type = None if success else random.choice([
            "rate_limit_exceeded", 
            "timeout", 
            "invalid_request", 
            "server_error"
        ])
        
        # Track the API call
        await cost_tracker.track_api_call(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            response_time_ms=response_time,
            success=success,
            error_type=error_type,
            user_id=f"user_{random.randint(1, 10)}",
            correlation_id=f"corr_{i:04d}"
        )
        
        # Small delay to spread out timestamps
        await asyncio.sleep(0.1)
    
    print(f"✅ Generated {num_calls} sample LLM API calls")


async def generate_historical_data(cost_tracker: LLMCostTracker, days_back: int = 7):
    """Generate historical data for trend analysis."""
    print(f"📊 Generating {days_back} days of historical data...")
    
    providers_models = [
        ("openai", "gpt-4"),
        ("openai", "gpt-3.5-turbo"),
        ("anthropic", "claude-3-opus"),
        ("anthropic", "claude-3-sonnet"),
    ]
    
    for day in range(days_back):
        # Generate calls for each day
        calls_per_day = random.randint(20, 100)
        base_time = datetime.now() - timedelta(days=day)
        
        for call in range(calls_per_day):
            provider, model = random.choice(providers_models)
            
            # Create API call with historical timestamp
            api_call = await cost_tracker.track_api_call(
                provider=provider,
                model=model,
                input_tokens=random.randint(100, 2000),
                output_tokens=random.randint(50, 1000),
                response_time_ms=random.uniform(300, 2000),
                success=random.random() > 0.03,
                user_id=f"user_{random.randint(1, 15)}"
            )
            
            # Manually adjust timestamp for historical data
            historical_time = base_time + timedelta(
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            api_call.timestamp = historical_time
    
    print(f"✅ Generated {days_back} days of historical data")


async def main():
    """Generate comprehensive sample data for the Observatory."""
    print("🚀 Starting Observatory sample data generation...")
    
    try:
        # Initialize configuration
        config = ObservatoryConfig()
        
        # Initialize components
        cost_tracker = LLMCostTracker(config)
        metrics_collector = MetricsCollector(config)
        analytics_engine = RealTimeAnalyticsEngine(config)
        
        # Start components (without Redis for this demo)
        print("📡 Starting components...")
        
        # Generate sample data
        await generate_sample_llm_calls(cost_tracker, num_calls=75)
        await generate_historical_data(cost_tracker, days_back=7)
        
        # Display results
        print("\n📊 Sample Data Summary:")
        print("=" * 50)
        
        # Cost tracking stats
        cost_stats = cost_tracker.get_tracking_stats()
        print(f"LLM API Calls Tracked: {cost_stats['calls_tracked']}")
        print(f"Total Cost Today: ${cost_stats['total_cost_today']:.4f}")
        print(f"Anomalies Detected: {cost_stats['anomalies_detected']}")
        
        # Provider breakdown
        print("\nCost by Provider:")
        for provider, cost in cost_stats['provider_costs'].items():
            print(f"  {provider}: ${cost:.4f}")
        
        # Cost metrics
        cost_metrics = cost_tracker.get_cost_metrics()
        print(f"\nProjected Monthly Cost: ${cost_metrics.projected_monthly_cost:.2f}")
        print(f"Cost Trend: {cost_metrics.cost_trend.value}")
        
        print("\n✅ Sample data generation complete!")
        print("\n💡 To see this data in the dashboard:")
        print("   1. Start the Observatory server: python -m src.beast_mode.observatory.server")
        print("   2. Open http://localhost:8000 in your browser")
        print("   3. The charts should now show the generated sample data")
        
    except Exception as e:
        print(f"❌ Error generating sample data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())