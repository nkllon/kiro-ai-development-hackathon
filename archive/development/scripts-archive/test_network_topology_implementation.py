#!/usr/bin/env python3
"""
Test script for Network Topology Discovery Implementation
========================================================

Simple test script to validate the NetworkTopologyDiscoverer implementation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_import():
    """Test basic imports."""
    try:
        from src.system_architecture.discovery.network_topology_discoverer import NetworkTopologyDiscoverer
        from src.system_architecture.models.network_topology import NetworkTopology, ServiceEndpoint, Protocol, ServiceStatus
        print("✅ Imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_initialization():
    """Test NetworkTopologyDiscoverer initialization."""
    try:
        from src.system_architecture.discovery.network_topology_discoverer import NetworkTopologyDiscoverer
        
        discoverer = NetworkTopologyDiscoverer()
        print("✅ Initialization successful")
        
        # Test module info
        info = discoverer.get_module_info()
        print(f"✅ Module info: {info['name']} v{info['version']}")
        
        # Test capabilities
        capabilities = discoverer.get_capabilities()
        print(f"✅ Capabilities: {len(capabilities)} capabilities")
        
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

def test_health_status():
    """Test health status functionality."""
    try:
        from src.system_architecture.discovery.network_topology_discoverer import NetworkTopologyDiscoverer
        
        discoverer = NetworkTopologyDiscoverer()
        health = discoverer.get_health_status()
        
        print(f"✅ Health status: {health.status.value}")
        print(f"✅ Health score: {health.health_score}")
        print(f"✅ Issues: {len(health.issues)}")
        
        return True
    except Exception as e:
        print(f"❌ Health status test failed: {e}")
        return False

def test_models():
    """Test network topology models."""
    try:
        from src.system_architecture.models.network_topology import (
            ServiceEndpoint, NetworkFlow, DNSMapping, RedisCoordination,
            WebSocketConfiguration, FailoverMechanism, NetworkTopology,
            Protocol, ServiceStatus, FlowType, FailoverType
        )
        
        # Test ServiceEndpoint creation
        endpoint = ServiceEndpoint(
            name="Test Service",
            host="localhost",
            port=8080,
            protocol=Protocol.TCP,
            status=ServiceStatus.ACTIVE
        )
        print(f"✅ ServiceEndpoint created: {endpoint.name}")
        
        # Test NetworkFlow creation
        flow = NetworkFlow(
            source="Internet",
            destination="Cloudflare Edge",
            protocol=Protocol.HTTPS,
            port=443,
            flow_type=FlowType.INGRESS
        )
        print(f"✅ NetworkFlow created: {flow.source} -> {flow.destination}")
        
        # Test DNSMapping creation
        mapping = DNSMapping(
            domain="test.example.com",
            target_service="Test Service",
            target_port=8080
        )
        print(f"✅ DNSMapping created: {mapping.domain}")
        
        # Test RedisCoordination creation
        redis = RedisCoordination(
            primary_endpoint="localhost:6379",
            health_status="healthy"
        )
        print(f"✅ RedisCoordination created: {redis.primary_endpoint}")
        
        # Test WebSocketConfiguration creation
        ws_config = WebSocketConfiguration(
            endpoint="/ws/test",
            upgrade_path="http://localhost:8080/ws/test"
        )
        print(f"✅ WebSocketConfiguration created: {ws_config.endpoint}")
        
        # Test FailoverMechanism creation
        failover = FailoverMechanism(
            mechanism_id="test_failover_001",
            failover_type=FailoverType.DNS_FAILOVER,
            description="Test failover mechanism",
            primary_target="Primary DNS",
            fallback_targets=["Fallback DNS"]
        )
        print(f"✅ FailoverMechanism created: {failover.mechanism_id}")
        
        # Test NetworkTopology creation
        topology = NetworkTopology(
            local_network_range="192.168.1.x",
            service_endpoints=[endpoint],
            network_flows=[flow],
            dns_mappings=[mapping],
            redis_coordination=redis,
            websocket_configs=[ws_config],
            failover_mechanisms=[failover]
        )
        print(f"✅ NetworkTopology created with {len(topology.service_endpoints)} endpoints")
        
        return True
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False

def test_discovery_methods():
    """Test discovery methods."""
    try:
        from src.system_architecture.discovery.network_topology_discoverer import NetworkTopologyDiscoverer
        
        discoverer = NetworkTopologyDiscoverer()
        
        # Test local network range discovery
        network_range = discoverer._discover_local_network_range()
        print(f"✅ Local network range: {network_range}")
        
        # Test port allocation mapping
        endpoints = [
            ServiceEndpoint(
                name="Test Service",
                host="localhost",
                port=8080,
                protocol=Protocol.TCP,
                status=ServiceStatus.ACTIVE
            )
        ]
        allocations = discoverer._map_port_allocations(endpoints)
        print(f"✅ Port allocations: {len(allocations)} ports mapped")
        
        # Test health endpoint retrieval
        health_endpoint = discoverer._get_health_endpoint("Observatory Server", 8888)
        print(f"✅ Health endpoint: {health_endpoint}")
        
        # Test WebSocket endpoints retrieval
        ws_endpoints = discoverer._get_websocket_endpoints("Observatory Server", 8888)
        print(f"✅ WebSocket endpoints: {len(ws_endpoints)} endpoints")
        
        return True
    except Exception as e:
        print(f"❌ Discovery methods test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Network Topology Discovery Implementation")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_import),
        ("Initialization Test", test_initialization),
        ("Health Status Test", test_health_status),
        ("Models Test", test_models),
        ("Discovery Methods Test", test_discovery_methods)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Implementation is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())