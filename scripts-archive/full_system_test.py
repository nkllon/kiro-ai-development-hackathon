#!/usr/bin/env python3
"""
Full System Test Suite for ReflectiveModule Auto-Registration
============================================================

Tests the complete system integration:
1. ReflectiveModule auto-registration patch
2. Smart container detection
3. Redis service discovery
4. Prometheus/Grafana integration
5. Multi-environment compatibility
"""

import sys
import os
import time
import json
import redis
import requests
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, '.')

def test_redis_connectivity():
    """Test Redis connectivity from host environment."""
    print("🔍 Testing Redis connectivity...")
    
    try:
        r = redis.Redis(host='localhost', port=6379, password='', decode_responses=True)
        result = r.ping()
        print(f"✅ Redis PING: {result}")
        
        # Test key operations
        test_key = f"system_test:{int(time.time())}"
        r.set(test_key, "test_value", ex=60)
        value = r.get(test_key)
        print(f"✅ Redis SET/GET: {value}")
        
        return True
    except Exception as e:
        print(f"❌ Redis connectivity failed: {e}")
        return False

def test_prometheus_connectivity():
    """Test Prometheus API connectivity."""
    print("🔍 Testing Prometheus connectivity...")
    
    try:
        response = requests.get("http://localhost:9090/api/v1/status/buildinfo", timeout=5)
        if response.status_code == 200:
            build_info = response.json()
            version = build_info['data']['version']
            print(f"✅ Prometheus version: {version}")
            return True
        else:
            print(f"❌ Prometheus returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Prometheus connectivity failed: {e}")
        return False

def test_grafana_connectivity():
    """Test Grafana API connectivity."""
    print("🔍 Testing Grafana connectivity...")
    
    try:
        response = requests.get("http://localhost:3000/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            version = health.get('version', 'unknown')
            print(f"✅ Grafana version: {version}")
            return True
        else:
            print(f"❌ Grafana returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Grafana connectivity failed: {e}")
        return False

def test_jaeger_connectivity():
    """Test Jaeger API connectivity."""
    print("🔍 Testing Jaeger connectivity...")
    
    try:
        response = requests.get("http://localhost:16686/api/services", timeout=5)
        if response.status_code == 200:
            services = response.json()
            print(f"✅ Jaeger services endpoint: {len(services.get('data', []))} services")
            return True
        else:
            print(f"❌ Jaeger returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Jaeger connectivity failed: {e}")
        return False

def test_reflective_module_registration():
    """Test ReflectiveModule auto-registration functionality."""
    print("🔍 Testing ReflectiveModule auto-registration...")
    
    try:
        from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, ModuleHealth, ModuleStatus, GracefulDegradationResult
        
        class SystemTestModule(ReflectiveModule):
            def get_module_info(self):
                return {'module_id': 'full_system_test', 'version': '1.0.0'}
            def get_capabilities(self):
                return [ModuleCapability.CORE_FUNCTIONALITY, ModuleCapability.MONITORING]
            def get_health_status(self):
                return ModuleHealth(
                    module_id='full_system_test',
                    status=ModuleStatus.HEALTHY, 
                    health_score=1.0, 
                    issues=[],
                    last_check=datetime.now(),
                    uptime_seconds=5, 
                    error_count=0, 
                    warning_count=0
                )
            def graceful_degradation(self):
                return GracefulDegradationResult(success=True, degraded_capabilities=[], remaining_capabilities=self.get_capabilities())
        
        print("   Creating test ReflectiveModule...")
        test_module = SystemTestModule()
        print("   ✅ ReflectiveModule created")
        
        # Give it time to register
        time.sleep(3)
        
        # Check Redis registration
        r = redis.Redis(host='localhost', port=6379, password='', decode_responses=True)
        
        # Check health key
        health_key = "health:full_system_test"
        health_data = r.hgetall(health_key)
        if health_data:
            print(f"   ✅ Health registration: {health_data['status']}")
        else:
            print("   ❌ Health registration failed")
            return False
        
        # Check service registry
        service_key = "service:registry:full_system_test"
        service_data = r.hgetall(service_key)
        if service_data:
            print(f"   ✅ Service registration: {service_data['module_type']}")
        else:
            print("   ❌ Service registration failed")
            return False
        
        # Check active modules
        active_modules = r.hgetall("beast_mode:active_modules")
        if "full_system_test" in active_modules:
            module_data = json.loads(active_modules["full_system_test"])
            print(f"   ✅ Active modules registration: {module_data['status']}")
        else:
            print("   ❌ Active modules registration failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ReflectiveModule registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_container_service_discovery():
    """Test that containerized services are discoverable."""
    print("🔍 Testing container service discovery...")
    
    try:
        r = redis.Redis(host='localhost', port=6379, password='', decode_responses=True)
        
        # Get all active modules
        active_modules = r.hgetall("beast_mode:active_modules")
        print(f"   📊 Total active modules: {len(active_modules)}")
        
        container_services = []
        host_services = []
        
        for module_id, module_data_str in active_modules.items():
            module_data = json.loads(module_data_str)
            
            # Detect container vs host based on hostname/PID patterns
            host = module_data.get('host', 'unknown')
            pid = module_data.get('pid', 0)
            
            if len(host) == 12 and host.isalnum():  # Docker container hostname pattern
                container_services.append({
                    'module_id': module_id,
                    'host': host,
                    'pid': pid,
                    'type': module_data.get('module_type')
                })
            else:
                host_services.append({
                    'module_id': module_id,
                    'host': host,
                    'pid': pid,
                    'type': module_data.get('module_type')
                })
        
        print(f"   🐳 Container services: {len(container_services)}")
        for service in container_services:
            print(f"      - {service['module_id']} ({service['type']}) on {service['host']}")
        
        print(f"   🏠 Host services: {len(host_services)}")
        for service in host_services:
            print(f"      - {service['module_id']} ({service['type']}) on {service['host']}")
        
        return len(container_services) > 0 and len(host_services) > 0
        
    except Exception as e:
        print(f"❌ Container service discovery failed: {e}")
        return False

def test_prometheus_service_discovery():
    """Test Prometheus service discovery integration."""
    print("🔍 Testing Prometheus service discovery...")
    
    try:
        response = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
        if response.status_code == 200:
            targets_data = response.json()
            targets = targets_data.get('data', {}).get('activeTargets', [])
            
            print(f"   📊 Prometheus targets: {len(targets)}")
            for target in targets:
                labels = target.get('labels', {})
                job = labels.get('job', 'unknown')
                instance = labels.get('instance', 'unknown')
                health = target.get('health', 'unknown')
                print(f"      - {job} ({instance}): {health}")
            
            return len(targets) > 0
        else:
            print(f"❌ Prometheus targets API returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Prometheus service discovery failed: {e}")
        return False

def test_system_integration():
    """Test full system integration capabilities."""
    print("🔍 Testing full system integration...")
    
    results = {
        'redis_services': 0,
        'prometheus_targets': 0,
        'grafana_health': False,
        'jaeger_health': False
    }
    
    try:
        # Count Redis services
        r = redis.Redis(host='localhost', port=6379, password='', decode_responses=True)
        active_modules = r.hgetall("beast_mode:active_modules")
        results['redis_services'] = len(active_modules)
        
        # Count Prometheus targets
        response = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
        if response.status_code == 200:
            targets_data = response.json()
            targets = targets_data.get('data', {}).get('activeTargets', [])
            results['prometheus_targets'] = len(targets)
        
        # Check Grafana health
        response = requests.get("http://localhost:3000/api/health", timeout=5)
        results['grafana_health'] = response.status_code == 200
        
        # Check Jaeger health
        response = requests.get("http://localhost:16686/api/services", timeout=5)
        results['jaeger_health'] = response.status_code == 200
        
        print(f"   📊 Integration Summary:")
        print(f"      Redis Services: {results['redis_services']}")
        print(f"      Prometheus Targets: {results['prometheus_targets']}")
        print(f"      Grafana Health: {'✅' if results['grafana_health'] else '❌'}")
        print(f"      Jaeger Health: {'✅' if results['jaeger_health'] else '❌'}")
        
        # Success criteria: At least 1 Redis service and all monitoring healthy
        success = (results['redis_services'] > 0 and 
                  results['grafana_health'] and 
                  results['jaeger_health'])
        
        return success
        
    except Exception as e:
        print(f"❌ System integration test failed: {e}")
        return False

def run_full_system_tests():
    """Run complete system test suite."""
    print("🚀 Starting Full System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Redis Connectivity", test_redis_connectivity),
        ("Prometheus Connectivity", test_prometheus_connectivity),
        ("Grafana Connectivity", test_grafana_connectivity),
        ("Jaeger Connectivity", test_jaeger_connectivity),
        ("ReflectiveModule Registration", test_reflective_module_registration),
        ("Container Service Discovery", test_container_service_discovery),
        ("Prometheus Service Discovery", test_prometheus_service_discovery),
        ("System Integration", test_system_integration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}")
        except Exception as e:
            results[test_name] = False
            print(f"   ❌ FAILED with exception: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 FULL SYSTEM TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is fully functional!")
        return True
    else:
        print("⚠️  Some tests failed - System has issues")
        return False

if __name__ == "__main__":
    success = run_full_system_tests()
    sys.exit(0 if success else 1)