#!/usr/bin/env python3
"""Quick streaming test"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
from beast_mode_resource_monitor import BeastModeResourceMonitor

async def quick_test():
    monitor = BeastModeResourceMonitor()
    
    print("🌊 Quick streaming test (5 updates)...")
    for i in range(5):
        await monitor._collect_gcp_billing_metrics()
        await monitor._collect_financial_metrics()
        
        unified = monitor.current_metrics.get('unified_financial')
        if unified:
            print(f"Update {i+1}: ${unified.total_cost_usd:.4f} total, ${unified.hourly_burn_rate:.4f}/hr")
        
        await asyncio.sleep(1)
    
    print("✅ Streaming test complete!")

if __name__ == "__main__":
    asyncio.run(quick_test())