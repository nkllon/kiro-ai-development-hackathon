#!/usr/bin/env python3
"""Test multi-service GCP billing integration"""

import asyncio
import sys
sys.path.append('src')

from beast_mode.billing.gcp_integration import GCPBillingMonitor

async def test_multi_service_billing():
    config = {
        'billing_account_id': 'test-account',
        'cache_duration_minutes': 15
    }
    
    monitor = GCPBillingMonitor(config)
    metrics = await monitor.collect_billing_metrics()
    
    print('=== MULTI-SERVICE GCP BILLING METRICS ===')
    print(f'Provider: {metrics.provider_name}')
    print(f'Daily Cost: ${metrics.daily_cost_usd:.4f}')
    print(f'Hourly Burn Rate: ${metrics.hourly_burn_rate:.4f}')
    print()
    
    print('=== COST BREAKDOWN ===')
    for service, cost in metrics.cost_breakdown.items():
        print(f'{service:25}: ${cost:.6f}')
    print()
    
    print('=== CORRELATION METRICS ===')
    usage = metrics.usage_metrics
    print(f'Cost per request:        ${usage["cost_per_request"]:.6f}')
    print(f'Cost per DB operation:   ${usage["cost_per_db_operation"]:.6f}')
    print(f'Cost per storage op:     ${usage["cost_per_storage_operation"]:.6f}')
    print(f'Cost per secret access:  ${usage["cost_per_secret_access"]:.6f}')
    print()
    
    print('=== USAGE METRICS ===')
    print(f'Cloud Run requests:      {usage["cloud_run_requests"]:,}')
    print(f'Cloud SQL operations:    {usage["cloud_sql_operations"]:,}')
    print(f'Storage operations:      {usage["storage_operations"]:,}')
    print(f'Secret access ops:       {usage["secret_access_operations"]:,}')
    print()
    
    print('=== OPTIMIZATION RECOMMENDATIONS ===')
    recommendations = monitor.get_cost_optimization_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f'{i}. [{rec["priority"].upper()}] {rec["title"]}')
        print(f'   Potential savings: ${rec["potential_savings_usd"]:.4f}/day')
        print(f'   Action: {rec["action"]}')
        print()

if __name__ == "__main__":
    asyncio.run(test_multi_service_billing())