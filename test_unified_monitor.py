#!/usr/bin/env python3
"""
Test Unified Resource Monitor

Test the Beast Mode resource monitor with GCP integration enabled
"""

import asyncio
import sys
import json
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from beast_mode_resource_monitor import BeastModeResourceMonitor

async def test_unified_monitor():
    """Test the unified resource monitor"""
    
    print("🧪 Testing Unified Beast Mode Resource Monitor")
    print("=" * 60)
    
    # Create test config with GCP enabled
    config_dir = Path('beast_mode_metrics')
    config_dir.mkdir(exist_ok=True)
    
    test_config = {
        'daily_budget_usd': 100.0,
        'alert_thresholds': {
            'hourly_burn_rate': 10.0,
            'token_cost_per_request': 0.20,
            'memory_usage_percent': 85.0,
            'cpu_usage_percent': 90.0,
            'gcp_daily_limit': 50.0
        },
        'llm_pricing': {
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002}
        },
        'gcp': {
            'enabled': True,
            'billing_account_id': 'test-account-123',
            'project_ids': ['test-project-1'],
            'cache_duration_minutes': 15,
            'budget_alerts': {
                'daily_limit_usd': 50.0,
                'hourly_spike_threshold': 10.0
            }
        },
        'update_interval_seconds': 1
    }
    
    # Save test config
    config_file = config_dir / 'monitor_config.json'
    with open(config_file, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    try:
        # Initialize monitor
        monitor = BeastModeResourceMonitor()
        print("✅ Monitor initialized successfully")
        
        if monitor.gcp_monitor:
            print("✅ GCP integration enabled")
        else:
            print("⚠️  GCP integration not available")
        
        # Add some mock token usage
        monitor.log_token_usage("openai", "gpt-4", 1500, 800, "test_request_1")
        monitor.log_token_usage("anthropic", "claude-3", 2000, 1200, "test_request_2")
        print("✅ Added mock LLM token usage")
        
        # Collect metrics once
        print("\n📊 Collecting metrics...")
        await monitor._collect_network_metrics()
        await monitor._collect_resource_metrics()
        await monitor._collect_gcp_billing_metrics()
        await monitor._collect_financial_metrics()
        
        # Display dashboard
        print("\n🖥️  Dashboard Preview:")
        print("=" * 60)
        await monitor._display_dashboard()
        
        # Test alerts
        await monitor._check_alerts()
        
        print("\n🎉 Unified monitor test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_unified_monitor())
    sys.exit(0 if success else 1)