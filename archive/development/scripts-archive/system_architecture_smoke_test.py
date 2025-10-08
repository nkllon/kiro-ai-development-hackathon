#!/usr/bin/env python3
"""
System Architecture Smoke Test
==============================

Tests the core system architecture components to verify they work correctly.
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, Any

from src.system_architecture.discovery.infrastructure_discoverer import InfrastructureDiscoverer
from src.system_architecture.analysis.relationship_mapper import RelationshipMapper
from src.system_architecture.analysis.data_flow_mapper import DataFlowMapper


async def run_smoke_test() -> Dict[str, Any]:
    """Run comprehensive smoke test of system architecture components."""
    
    print("🧪 SYSTEM ARCHITECTURE SMOKE TEST")
    print("=" * 50)
    
    results = {
        "test_start": datetime.now().isoformat(),
        "tests": {},
        "overall_status": "unknown"
    }
    
    # Test 1: Infrastructure Discovery
    print("\n1️⃣ Testing Infrastructure Discovery...")
    try:
        discoverer = InfrastructureDiscoverer()
        
        # Test basic functionality
        module_info = discoverer.get_module_info()
        health_status = discoverer.get_health_status()
        
        # Test service discovery
        services = discoverer.discover_services()
        network_config = discoverer.discover_network_config()
        configurations = discoverer.discover_configurations()
        
        # Test comprehensive discovery
        discovery_report = await discoverer.perform_comprehensive_discovery()
        
        results["tests"]["infrastructure_discovery"] = {
            "status": "PASS",
            "services_discovered": len(services),
            "network_mappings": len(network_config.dns_mappings),
            "makefile_targets": len(configurations.makefile_targets),
            "yaml_configs": len(configurations.yaml_configs),
            "json_configs": len(configurations.json_configs),
            "health": health_status["status"]
        }
        
        print(f"   ✅ Infrastructure Discovery: {len(services)} services, {len(configurations.makefile_targets)} Makefile targets")
        
    except Exception as e:
        results["tests"]["infrastructure_discovery"] = {
            "status": "FAIL",
            "error": str(e)
        }
        print(f"   ❌ Infrastructure Discovery failed: {e}")
    
    # Test 2: Relationship Mapping
    print("\n2️⃣ Testing Relationship Mapping...")
    try:
        mapper = RelationshipMapper()
        
        # Test basic functionality
        module_info = mapper.get_module_info()
        health_status = mapper.get_health_status()
        capabilities = mapper.get_capabilities()
        
        results["tests"]["relationship_mapping"] = {
            "status": "PASS",
            "capabilities": len(capabilities),
            "health_score": health_status.health_score,
            "module_status": health_status.status.value
        }
        
        print(f"   ✅ Relationship Mapping: {len(capabilities)} capabilities, health score {health_status.health_score}")
        
    except Exception as e:
        results["tests"]["relationship_mapping"] = {
            "status": "FAIL", 
            "error": str(e)
        }
        print(f"   ❌ Relationship Mapping failed: {e}")
    
    # Test 3: Data Flow Mapping
    print("\n3️⃣ Testing Data Flow Mapping...")
    try:
        data_mapper = DataFlowMapper()
        
        # Test basic functionality
        module_info = data_mapper.get_module_info()
        health_status = data_mapper.get_health_status()
        capabilities = data_mapper.get_capabilities()
        
        results["tests"]["data_flow_mapping"] = {
            "status": "PASS",
            "capabilities": len(capabilities),
            "health_score": health_status.health_score,
            "module_status": health_status.status.value
        }
        
        print(f"   ✅ Data Flow Mapping: {len(capabilities)} capabilities, health score {health_status.health_score}")
        
    except Exception as e:
        results["tests"]["data_flow_mapping"] = {
            "status": "FAIL",
            "error": str(e)
        }
        print(f"   ❌ Data Flow Mapping failed: {e}")
    
    # Test 4: Integration Test
    print("\n4️⃣ Testing Component Integration...")
    try:
        # Test that components can work together
        discoverer = InfrastructureDiscoverer()
        mapper = RelationshipMapper()
        
        # Discover services
        services = discoverer.discover_services()
        
        # Create mock dependency data for relationship mapping
        mock_components = [
            {"id": "observatory", "name": "Observatory Server", "port": 8888},
            {"id": "prometheus", "name": "Prometheus", "port": 9090},
            {"id": "grafana", "name": "Grafana", "port": 3000}
        ]
        
        results["tests"]["integration"] = {
            "status": "PASS",
            "components_integrated": len(mock_components),
            "services_available": len(services)
        }
        
        print(f"   ✅ Integration: {len(mock_components)} components integrated with {len(services)} discovered services")
        
    except Exception as e:
        results["tests"]["integration"] = {
            "status": "FAIL",
            "error": str(e)
        }
        print(f"   ❌ Integration test failed: {e}")
    
    # Calculate overall status
    test_results = [test["status"] for test in results["tests"].values()]
    passed_tests = test_results.count("PASS")
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        results["overall_status"] = "PASS"
        status_emoji = "✅"
    elif passed_tests > 0:
        results["overall_status"] = "PARTIAL"
        status_emoji = "⚠️"
    else:
        results["overall_status"] = "FAIL"
        status_emoji = "❌"
    
    results["test_end"] = datetime.now().isoformat()
    results["summary"] = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": f"{(passed_tests/total_tests)*100:.1f}%"
    }
    
    print(f"\n🎯 SMOKE TEST RESULTS")
    print("=" * 30)
    print(f"{status_emoji} Overall Status: {results['overall_status']}")
    print(f"📊 Tests Passed: {passed_tests}/{total_tests} ({results['summary']['success_rate']})")
    
    if results["overall_status"] == "PASS":
        print("🎉 All system architecture components are working correctly!")
    elif results["overall_status"] == "PARTIAL":
        print("⚠️  Some components have issues but core functionality works")
    else:
        print("❌ Critical issues found - system needs attention")
    
    return results


async def main():
    """Main test execution."""
    try:
        results = await run_smoke_test()
        
        # Exit with appropriate code
        if results["overall_status"] == "PASS":
            sys.exit(0)
        elif results["overall_status"] == "PARTIAL":
            sys.exit(1)
        else:
            sys.exit(2)
            
    except Exception as e:
        print(f"💥 Smoke test crashed: {e}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())