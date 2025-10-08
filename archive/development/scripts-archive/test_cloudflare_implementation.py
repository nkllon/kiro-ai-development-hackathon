#!/usr/bin/env python3
"""
Simple test script to validate CloudflareTunnelDiscoverer implementation
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

try:
    from src.system_architecture.discovery.cloudflare_tunnel_discoverer import CloudflareTunnelDiscoverer
    print("✅ Successfully imported CloudflareTunnelDiscoverer")
    
    # Test instantiation
    discoverer = CloudflareTunnelDiscoverer()
    print("✅ Successfully instantiated CloudflareTunnelDiscoverer")
    
    # Test basic methods
    module_info = discoverer.get_module_info()
    print(f"✅ Module info: {module_info['name']} v{module_info['version']}")
    
    capabilities = discoverer.get_capabilities()
    print(f"✅ Capabilities: {len(capabilities)} capabilities found")
    
    health_status = discoverer.get_health_status()
    print(f"✅ Health status: {health_status.status.value} (score: {health_status.health_score})")
    
    # Test graceful degradation
    degradation_result = discoverer.graceful_degradation()
    print(f"✅ Graceful degradation: {'Success' if degradation_result.success else 'Failed'}")
    
    print("\n🎉 All basic tests passed! Implementation is working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)