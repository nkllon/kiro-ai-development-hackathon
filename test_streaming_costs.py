#!/usr/bin/env python3
"""
Test Streaming Cost Updates for Cloud Run

Demonstrates real-time cost streaming for pay-per-transaction model
"""

import asyncio
import sys
import json
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from beast_mode_resource_monitor import BeastModeResourceMonitor

def cost_update_callback(update):
    """Handle streaming cost updates"""
    print(f"📊 STREAM UPDATE #{update['update_count']:03d}")
    print(f"   💰 Total: ${update['total_cost']:.4f}")
    print(f"   🚀 GCP (Cloud Run): ${update['gcp_cost']:.4f}")
    print(f"   🤖 LLM: ${update['llm_cost']:.4f}")
    print(f"   🔥 Burn Rate: ${update['hourly_rate']:.4f}/hour")
    print(f"   🎯 Budget Left: ${update['budget_remaining']:.2f}")
    print(f"   ⏰ {update['timestamp']}")
    print("   " + "─" * 40)

async def test_streaming_costs():
    """Test real-time cost streaming"""
    
    print("🌊 Testing Real-Time Cost Streaming for Cloud Run")
    print("=" * 60)
    print("This simulates pay-per-transaction cost updates")
    print("Press Ctrl+C to stop streaming")
    print("=" * 60)
    
    # Create test config with GCP enabled
    config_dir = Path('beast_mode_metrics')
    config_dir.mkdir(exist_ok=True)
    
    test_config = {
        'daily_budget_usd': 25.0,  # Smaller budget for Cloud Run
        'gcp': {
            'enabled': True,
            'billing_account_id': 'cloudrun-test-123',
            'project_ids': ['beast-mode-cloudrun'],
            'cache_duration_minutes': 1,  # Faster updates for streaming
            'budget_alerts': {
                'daily_limit_usd': 20.0,
                'hourly_spike_threshold': 2.0
            }
        },
        'update_interval_seconds': 2
    }
    
    # Save test config
    config_file = config_dir / 'monitor_config.json'
    with open(config_file, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    try:
        # Initialize monitor
        monitor = BeastModeResourceMonitor()
        
        # Add some LLM usage for comparison
        monitor.log_token_usage("openai", "gpt-4", 500, 300, "cloudrun_request_1")
        
        # Start streaming (will run until Ctrl+C)
        await monitor.stream_cost_updates(callback=cost_update_callback)
        
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        asyncio.run(test_streaming_costs())
    except KeyboardInterrupt:
        print("\n🎉 Streaming test completed!")
        sys.exit(0)