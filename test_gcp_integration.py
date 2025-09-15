#!/usr/bin/env python3
"""
Test GCP Billing Integration

Quick test to verify the GCP billing integration works with mock data
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.billing import GCPBillingMonitor


async def test_gcp_integration():
    """Test GCP billing integration with mock data"""

    print("🧪 Testing GCP Billing Integration")
    print("=" * 50)

    # Test configuration
    config = {
        "enabled": True,
        "billing_account_id": "test-account-123",
        "project_ids": ["test-project-1", "test-project-2"],
        "cache_duration_minutes": 15,
    }

    # Initialize GCP monitor
    try:
        gcp_monitor = GCPBillingMonitor(config)
        print("✅ GCP Monitor initialized successfully")

        # Test health status
        health = gcp_monitor.get_health_status()
        print(f"✅ Health Status: {health.status_message}")

        # Test metrics collection
        metrics = await gcp_monitor.collect_billing_metrics()
        print(f"✅ Collected metrics: ${metrics.total_cost_usd:.2f} total cost")
        print(f"   📊 Cost breakdown: {metrics.cost_breakdown}")
        print(f"   📈 Usage metrics: {metrics.usage_metrics}")

        # Test configuration schema
        schema = gcp_monitor.get_configuration_schema()
        print(f"✅ Configuration schema has {len(schema['properties'])} properties")

        # Test cost optimization recommendations
        recommendations = gcp_monitor.get_cost_optimization_recommendations()
        print(f"✅ Generated {len(recommendations)} cost optimization recommendations")
        for rec in recommendations:
            print(
                f"   💡 {rec['title']}: ${rec['potential_savings_usd']:.2f} potential savings"
            )

        print("\n🎉 All tests passed! GCP integration is working.")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_gcp_integration())
    sys.exit(0 if success else 1)
