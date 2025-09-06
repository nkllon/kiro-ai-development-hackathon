#!/usr/bin/env python3
"""
Test Cost Correlation Analysis

Demonstrates how Cloud Run costs correlate with transaction count
"""

import asyncio
import sys
import json
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from beast_mode_resource_monitor import BeastModeResourceMonitor

async def analyze_cost_correlation():
    """Analyze cost correlation with transaction count"""
    
    print("🧮 Cloud Run Cost Correlation Analysis")
    print("=" * 60)
    print("Analyzing how costs correlate with transaction volume")
    print("=" * 60)
    
    # Create test config
    config_dir = Path('beast_mode_metrics')
    config_dir.mkdir(exist_ok=True)
    
    test_config = {
        'daily_budget_usd': 10.0,
        'gcp': {
            'enabled': True,
            'billing_account_id': 'correlation-test-123',
            'project_ids': ['cost-correlation-analysis'],
            'cache_duration_minutes': 1
        }
    }
    
    config_file = config_dir / 'monitor_config.json'
    with open(config_file, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    try:
        monitor = BeastModeResourceMonitor()
        
        print("📊 Collecting multiple samples to analyze correlation...")
        
        samples = []
        for i in range(5):
            await monitor._collect_gcp_billing_metrics()
            
            gcp_billing = monitor.current_metrics.get('gcp_billing')
            if gcp_billing and gcp_billing.usage_metrics:
                usage = gcp_billing.usage_metrics
                sample = {
                    'requests': usage.get('cloud_run_requests', 0),
                    'total_cost': gcp_billing.daily_cost_usd,
                    'cost_per_request': usage.get('cost_per_request', 0),
                    'cpu_seconds': usage.get('cpu_seconds', 0),
                    'memory_gb_seconds': usage.get('memory_gb_seconds', 0),
                    'data_transfer_gb': usage.get('data_transfer_gb', 0)
                }
                samples.append(sample)
                
                print(f"\nSample {i+1}:")
                print(f"  🚀 Requests: {sample['requests']:,}")
                print(f"  💰 Total Cost: ${sample['total_cost']:.6f}")
                print(f"  📊 Cost/Request: ${sample['cost_per_request']:.6f}")
                print(f"  ⚡ CPU Seconds: {sample['cpu_seconds']:.1f}")
                print(f"  🧠 Memory GB-Sec: {sample['memory_gb_seconds']:.1f}")
                print(f"  🌐 Data Transfer: {sample['data_transfer_gb']:.3f} GB")
        
        # Analyze correlation
        if len(samples) >= 2:
            print("\n🔍 CORRELATION ANALYSIS:")
            print("=" * 40)
            
            # Calculate average cost per request
            avg_cost_per_request = sum(s['cost_per_request'] for s in samples) / len(samples)
            print(f"📊 Average Cost/Request: ${avg_cost_per_request:.6f}")
            
            # Calculate cost components
            total_requests = sum(s['requests'] for s in samples)
            total_cost = sum(s['total_cost'] for s in samples)
            total_cpu = sum(s['cpu_seconds'] for s in samples)
            
            if total_requests > 0:
                print(f"📈 Total Requests: {total_requests:,}")
                print(f"💰 Total Cost: ${total_cost:.6f}")
                print(f"⚡ Total CPU Seconds: {total_cpu:.1f}")
                print(f"🧮 CPU Seconds/Request: {total_cpu/total_requests:.3f}")
                
                # Cost breakdown analysis
                print(f"\n💡 INSIGHTS:")
                if avg_cost_per_request < 0.0001:
                    print(f"   ✅ Very efficient: <$0.0001 per request")
                elif avg_cost_per_request < 0.001:
                    print(f"   ✅ Efficient: <$0.001 per request")
                else:
                    print(f"   ⚠️  High cost per request: >${avg_cost_per_request:.6f}")
                
                cpu_per_request = total_cpu / total_requests
                if cpu_per_request < 0.1:
                    print(f"   ✅ Fast execution: {cpu_per_request:.3f}s per request")
                elif cpu_per_request < 0.5:
                    print(f"   ⚠️  Moderate execution: {cpu_per_request:.3f}s per request")
                else:
                    print(f"   🚨 Slow execution: {cpu_per_request:.3f}s per request")
        
        print(f"\n🎉 Cost correlation analysis complete!")
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(analyze_cost_correlation())
    sys.exit(0 if success else 1)