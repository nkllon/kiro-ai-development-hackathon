#!/usr/bin/env python3
"""
Comprehensive Auto-Registration Test Suite
==========================================

This test demonstrates the complete ReflectiveModule auto-registration system:
1. Smart environment detection (host vs container)
2. Automatic Redis host resolution
3. Service registration in Redis
4. Health monitoring integration
5. Multi-environment compatibility
"""

import sys
import os
import time
import json
import redis
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, '.')

def test_smart_environment_detection():
    """Test the smart environment detection logic."""
    print("🔍 Testing Smart Environment Detection")
    print("-" * 40)
    
    from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
    
    # Test the detection logic directly
    test_module = ReflectiveModule()
    
    # Check environment detection
    is_container = test_module._is_running_in_container()
    is_k8s = test_module._is_running_in_kubernetes()
    redis_host = test_module._get_redis_host()
    
    print(f"   Container Detection: {'✅ Container' if is_container else '❌ Host'}")
    print(f"   Kubernetes Detection: {'✅ K8s' if is_k8s else '❌ Not K8s'}")
    print(f"   Redis Host Resolution: {redis_host}")
    print(f"   Docker env file exists: {os.path.exists('/.dockerenv')}")
    print(f"   KUBERNETES_SERVICE_HOST: {os.getenv('KUBERNETES_SERVICE_HOST', 'Not set')}")
    
    return True

def test_redis_registration_data():
    """Test the structure and content of Redis registration data."""
    print("\n🔍 Testing Redis Registration Data Structure")
    print("-" * 40)
    
    try:
        r = redis.Redis(host='localhost', port=6379, password='', decode_responses=True)
        
        # Get all active modules
        active_modules = r.hgetall("beast_mode:active_modules")
        print(f"   📊 Total registered modules: {len(active_modules)}")
        
        for module_id, module_data_str in active_modules.items():
            module_data = json.loads(module_data_str)
            print(f"\n   🧩 Module: {module_id}")
            print(f"      Type: {module_data.get('module_type', 'unknown')}")
            print(f"      Host: {module_data.get('host', 'unknown')}")
            print(f"      PID: {module_data.get('pid', 'unknown')}")
            print(f"      Status: {module_data.get('status', 'unknown')}")
            print(f"      Capabilities: {module_data.get('capabilities', [])}")
            print(f"      Registered: {module_data.get('registered_at', 'unknown')}")
            
            # Check if this is a container service
            host = module_data.get('host', '')
            if len(host) == 12 and host.isalnum():
                print(f"      🐳 Container ID: {host}")
            else:
                print(f"      🏠 Host service")
        
        return len(active_modules) > 0
        
    except Exception as e:
        print(f"   ❌ Redis registration test failed: {e}")
        return False

def test_health_monitoring_integration():
    """Test health monitoring data in Redis."""
    print("\n🔍 Testing Health Monitoring Integration")
    print("-" * 40)
    
    try:
        r = redis.Redis(host='localhost', port=6379, password='', decode_responses=True)
        
        # Get all health keys
        health_keys = r.keys("health:*")
        print(f"   📊 Health monitoring entries: {len(health_keys)}")
        
        for health_key in health_keys:
            module_id = health_key.replace("health:", "")
            health_data = r.hgetall(health_key)
            
            print(f"\n   💚 Health: {module_id}")
            print(f"      Status: {health_data.get('status', 'unknown')}")
            print(f"      Score: {health_data.get('health_score', 'unknown')}")
            print(f"      Last Check: {health_data.get('last_check', 'unknown')}")
            print(f"      Uptime: {health_data.get('uptime_seconds', 'unknown')}s")
        
        return len(health_keys) > 0
        
    except Exception as e:
        print(f"   ❌ Health monitoring test failed: {e}")
        return False

def test_service_registry_integration():
    """Test service registry data structure."""
    print("\n🔍 Testing Service Registry Integration")
    print("-" * 40)
    
    try:
        r = redis.Redis(host='localhost', port=6379, password='', decode_responses=True)
        
        # Get all service registry keys
        service_keys = r.keys("service:registry:*")
        print(f"   📊 Service registry entries: {len(service_keys)}")
        
        for service_key in service_keys:
            module_id = service_key.replace("service:registry:", "")
            service_data = r.hgetall(service_key)
            
            print(f"\n   🔧 Service: {module_id}")
            print(f"      Module Type: {service_data.get('module_type', 'unknown')}")
            print(f"      Capabilities: {service_data.get('capabilities', 'unknown')}")
            print(f"      Host: {service_data.get('host', 'unknown')}")
            print(f"      PID: {service_data.get('pid', 'unknown')}")
            print(f"      Registered: {service_data.get('registered_at', 'unknown')}")
        
        return len(service_keys) > 0
        
    except Exception as e:
        print(f"   ❌ Service registry test failed: {e}")
        return False

def test_container_vs_host_services():
    """Test that we can distinguish container vs host services."""
    print("\n🔍 Testing Container vs Host Service Detection")
    print("-" * 40)
    
    try:
        r = redis.Redis(host='localhost', port=6379, password='', decode_responses=True)
        
        active_modules = r.hgetall("beast_mode:active_modules")
        
        container_services = []
        host_services = []
        
        for module_id, module_data_str in active_modules.items():
            module_data = json.loads(module_data_str)
            host = module_data.get('host', 'unknown')
            
            # Docker container hostnames are typically 12-character hex strings
            if len(host) == 12 and host.isalnum():
                container_services.append({
                    'module_id': module_id,
                    'host': host,
                    'type': module_data.get('module_type')
                })
            else:
                host_services.append({
                    'module_id': module_id,
                    'host': host,
                    'type': module_data.get('module_type')
                })
        
        print(f"   🐳 Container Services: {len(container_services)}")
        for service in container_services:
            print(f"      - {service['module_id']} ({service['type']}) on {service['host']}")
        
        print(f"   🏠 Host Services: {len(host_services)}")
        for service in host_services:
            print(f"      - {service['module_id']} ({service['type']}) on {service['host']}")
        
        # Success if we have both types
        success = len(container_services) > 0 and len(host_services) > 0
        print(f"\n   {'✅' if success else '❌'} Multi-environment detection: {'Working' if success else 'Failed'}")
        
        return success
        
    except Exception as e:
        print(f"   ❌ Container vs host detection failed: {e}")
        return False

def test_live_registration():
    """Test live registration by creating a new module."""
    print("\n🔍 Testing Live Registration")
    print("-" * 40)
    
    try:
        from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, ModuleHealth, ModuleStatus, GracefulDegradationResult
        
        class LiveTestModule(ReflectiveModule):
            def get_module_info(self):
                return {'module_id': 'live_test_module', 'version': '1.0.0'}
            def get_capabilities(self):
                return [ModuleCapability.CORE_FUNCTIONALITY]
            def get_health_status(self):
                return ModuleHealth(
                    module_id='live_test_module',
                    status=ModuleStatus.HEALTHY, 
                    health_score=1.0, 
                    issues=[],
                    last_check=datetime.now(),
                    uptime_seconds=1, 
                    error_count=0, 
                    warning_count=0
                )
            def graceful_degradation(self):
                return GracefulDegradationResult(success=True, degraded_capabilities=[], remaining_capabilities=self.get_capabilities())
        
        print("   🧠 Creating live test module...")
        
        # Get initial count
        r = redis.Redis(host='localhost', port=6379, password='', decode_responses=True)
        initial_count = len(r.hgetall("beast_mode:active_modules"))
        print(f"   📊 Initial module count: {initial_count}")
        
        # Create module
        test_module = LiveTestModule()
        print("   ✅ Module created")
        
        # Wait for registration
        time.sleep(2)
        
        # Check new count
        final_count = len(r.hgetall("beast_mode:active_modules"))
        print(f"   📊 Final module count: {final_count}")
        
        # Check specific registration
        module_data = r.hget("beast_mode:active_modules", "live_test_module")
        if module_data:
            data = json.loads(module_data)
            print(f"   ✅ Live registration successful: {data['status']}")
            return True
        else:
            print("   ❌ Live registration failed")
            return False
        
    except Exception as e:
        print(f"   ❌ Live registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_tests():
    """Run all comprehensive auto-registration tests."""
    print("🚀 Comprehensive Auto-Registration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Smart Environment Detection", test_smart_environment_detection),
        ("Redis Registration Data", test_redis_registration_data),
        ("Health Monitoring Integration", test_health_monitoring_integration),
        ("Service Registry Integration", test_service_registry_integration),
        ("Container vs Host Detection", test_container_vs_host_services),
        ("Live Registration", test_live_registration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            results[test_name] = False
            print(f"   ❌ Test failed with exception: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 COMPREHENSIVE TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Auto-registration system is fully functional!")
        return True
    else:
        print("⚠️  Some tests failed - System has issues")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)