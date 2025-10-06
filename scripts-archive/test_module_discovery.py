#!/usr/bin/env python3
"""
Test script for the Module Discovery Engine.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.observatory.module_discovery import ModuleDiscoveryEngine


async def main():
    """Test the Module Discovery Engine."""
    print("🔍 Testing Module Discovery Engine...")
    
    try:
        # Create discovery engine
        discovery_engine = ModuleDiscoveryEngine()
        
        # Discover modules
        print("\n📡 Discovering Beast Mode modules...")
        modules = await discovery_engine.discover_reflective_modules()
        
        # Display results
        print(f"\n✅ Discovery Results:")
        print(f"   Total modules found: {len(modules)}")
        
        # Show modules with metrics
        metrics_modules = discovery_engine.get_modules_with_metrics()
        print(f"   Modules with get_metrics(): {len(metrics_modules)}")
        
        # Display discovered modules
        print(f"\n📋 Discovered Modules:")
        for module_id, module_info in modules.items():
            status = "✅" if module_info.instance else "⚠️"
            metrics = "📊" if module_info.has_get_metrics else "  "
            health = "💚" if module_info.has_get_health_status else "  "
            
            print(f"   {status} {metrics} {health} {module_id}")
            if module_info.discovery_errors:
                for error in module_info.discovery_errors:
                    print(f"      ⚠️ {error}")
        
        # Show discovery stats
        stats = discovery_engine.get_discovery_stats()
        print(f"\n📊 Discovery Statistics:")
        print(f"   Success rate: {stats['discovery_success_rate']:.1f}%")
        print(f"   Discovery errors: {stats['discovery_errors']}")
        print(f"   Modules with metrics: {stats['modules_with_metrics']}")
        
        # Test health status
        health = discovery_engine.get_health_status()
        print(f"\n💚 Discovery Engine Health:")
        print(f"   Status: {health.status.value}")
        print(f"   Health score: {health.health_score}")
        print(f"   Issues: {health.issues}")
        
        print(f"\n🎯 Module Discovery Test Complete!")
        
    except Exception as e:
        print(f"❌ Error testing module discovery: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())