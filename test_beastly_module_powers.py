#!/usr/bin/env python3
"""
🐺 BEASTLY MODULE POWER TEST 🐺
Testing if the Beastly Module actually gives us observability superpowers!
"""

import time
import asyncio
from datetime import datetime

# 🐺 Import from the Beastly Module (unified core)
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus

class BeastlyTestModule(ReflectiveModule):
    """🐺 A test module with beastly observability powers!"""
    
    def __init__(self):
        super().__init__()
        self.test_counter = 0
        self.start_time = datetime.now()
        print("🐺 Beastly Module initialized! Checking for superpowers...")
    
    def do_some_work(self):
        """Simulate some work to generate metrics."""
        self.test_counter += 1
        print(f"🔥 Doing beastly work #{self.test_counter}")
        time.sleep(0.1)  # Simulate work
        return f"Work completed: {self.test_counter}"
    
    def get_health_status(self) -> ModuleHealth:
        """Override health status for testing."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return ModuleHealth(
            module_id="beastly_test_module",
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=0,
            warning_count=0
        )
    
    def get_capabilities(self):
        """Return beastly capabilities."""
        return ["BEASTLY_TESTING", "METRICS_GENERATION", "HEALTH_MONITORING"]
    
    def get_module_info(self):
        """Return module information."""
        return {
            "name": "BeastlyTestModule",
            "version": "1.0.0",
            "description": "🐺 Testing beastly observability powers",
            "type": "test_module"
        }
    
    def graceful_degradation(self, error):
        """Handle graceful degradation."""
        print(f"🐺 Beastly graceful degradation activated for error: {error}")
        return {"status": "degraded", "message": "Still beastly, just slower! 🐺"}

async def main():
    """Test the Beastly Module powers!"""
    print("="*60)
    print("🐺 BEASTLY MODULE POWER TEST STARTING 🐺")
    print("="*60)
    
    # Create our beastly module
    beast = BeastlyTestModule()
    
    # Test basic functionality
    print("\n1. Testing basic beastly functionality...")
    for i in range(3):
        result = beast.do_some_work()
        print(f"   Result: {result}")
    
    # Test health status
    print("\n2. Testing beastly health status...")
    health = beast.get_health_status()
    print(f"   Status: {health.status}")
    print(f"   Health Score: {health.health_score}")
    print(f"   Uptime: {health.uptime_seconds:.1f}s")
    print(f"   Issues: {health.issues}")
    print(f"   🐺 BEASTLY HEALTH CONFIRMED!")
    
    # Test if we have the expected beastly methods
    print("\n3. Checking for beastly superpowers...")
    beastly_methods = [
        'get_health_status',
        'get_capabilities', 
        'get_metrics',
        'graceful_degradation'
    ]
    
    for method in beastly_methods:
        if hasattr(beast, method):
            print(f"   ✅ {method} - BEASTLY POWER DETECTED! 🐺")
        else:
            print(f"   ❌ {method} - Missing beastly power")
    
    # Test metrics endpoint (if available)
    print("\n4. Testing metrics generation...")
    try:
        if hasattr(beast, 'get_metrics'):
            metrics = beast.get_metrics()
            print(f"   📊 Metrics generated: {len(metrics) if metrics else 0} metrics")
            if metrics:
                for key, value in metrics.items():
                    print(f"      {key}: {value}")
        else:
            print("   📊 No get_metrics method found")
    except Exception as e:
        print(f"   ⚠️ Metrics error: {e}")
    
    # Test if Prometheus registration happened
    print("\n5. Checking for Prometheus registration...")
    try:
        # Check if the module registered itself somehow
        print(f"   🔍 Module ID: {getattr(beast, 'module_id', 'Not found')}")
        print(f"   🔍 Component name: {getattr(beast, 'component_name', 'Not found')}")
        
        # Look for any prometheus-related attributes
        prometheus_attrs = [attr for attr in dir(beast) if 'prometheus' in attr.lower() or 'metric' in attr.lower()]
        if prometheus_attrs:
            print(f"   📈 Prometheus-related attributes: {prometheus_attrs}")
        else:
            print("   📈 No obvious Prometheus attributes found")
            
    except Exception as e:
        print(f"   ⚠️ Prometheus check error: {e}")
    
    print("\n" + "="*60)
    print("🐺 BEASTLY MODULE TEST COMPLETE! 🐺")
    print("="*60)
    
    # Keep running for a bit to see if any background registration happens
    print("\n⏰ Keeping module alive for 10 seconds to check for background magic...")
    for i in range(10):
        print(f"   Heartbeat {i+1}/10 - Module still beastly! 🐺")
        time.sleep(1)
    
    print("\n🎯 Test complete! Check if any metrics appeared in Prometheus/Grafana!")

if __name__ == "__main__":
    asyncio.run(main())