#!/usr/bin/env python3
"""
Unit Tests for Network Topology Discoverer - Task 1.6
====================================================

Comprehensive unit tests for NetworkTopologyDiscoverer with >90% coverage.
Tests all discovery methods, error handling, and ReflectiveModule integration.

Author: Beast Mode Framework
Date: 2024-12-19
Version: 1.0
"""

import pytest
import socket
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, List, Any

from src.system_architecture.discovery.network_topology_discoverer import NetworkTopologyDiscoverer
from src.system_architecture.models.network_topology import (
    NetworkTopology,
    ServiceEndpoint,
    NetworkFlow,
    DNSMapping,
    RedisCoordination,
    WebSocketConfiguration,
    FailoverMechanism,
    ServiceStatus,
    Protocol,
    FlowType,
    FailoverType
)


class TestNetworkTopologyDiscoverer:
    """Test suite for NetworkTopologyDiscoverer class."""
    
    @pytest.fixture
    def discoverer(self):
        """Create NetworkTopologyDiscoverer instance for testing."""
        config = {
            'scan_timeout': 1.0,
            'max_concurrent_scans': 5
        }
        return NetworkTopologyDiscoverer(config)
    
    @pytest.fixture
    def mock_topology(self):
        """Create mock network topology for testing."""
        return NetworkTopology(
            local_network_range="192.168.1.x",
            service_endpoints=[
                ServiceEndpoint(
                    name="Observatory Server",
                    host="localhost",
                    port=8888,
                    protocol=Protocol.TCP,
                    status=ServiceStatus.ACTIVE,
                    response_time_ms=50.0,
                    health_endpoint="/health",
                    websocket_endpoints=["/ws/observatory", "/ws/emoji-rain"],
                    last_checked=datetime.now()
                ),
                ServiceEndpoint(
                    name="Prometheus",
                    host="localhost",
                    port=9090,
                    protocol=Protocol.TCP,
                    status=ServiceStatus.ACTIVE,
                    response_time_ms=30.0,
                    health_endpoint="/metrics",
                    last_checked=datetime.now()
                )
            ],
            network_flows=[
                NetworkFlow(
                    source="Internet",
                    destination="Cloudflare Edge",
                    protocol=Protocol.HTTPS,
                    port=443,
                    flow_type=FlowType.INGRESS,
                    decision_points=["DNS Resolution", "SSL/TLS Handshake"],
                    routing_rules=[{"condition": "domain == observatory.nkllon.com", "target": "localhost:8888"}]
                )
            ],
            dns_mappings=[
                DNSMapping(
                    domain="observatory.nkllon.com",
                    target_service="Observatory Server",
                    target_port=8888,
                    tunnel_id="d1e53e43-033f-4994-8f46-c83962ae3785",
                    failover_targets=["direct-ip-access"],
                    ttl_seconds=300
                )
            ],
            redis_coordination=RedisCoordination(
                primary_endpoint="192.168.1.119:6379",
                fallback_endpoints=["localhost:6380"],
                cluster_mode=False,
                health_status="healthy",
                last_health_check=datetime.now()
            ),
            websocket_configs=[
                WebSocketConfiguration(
                    endpoint="/ws/observatory",
                    upgrade_path="http://localhost:8888/ws/observatory",
                    supported_protocols=["websocket"],
                    connection_flow=["HTTP Request", "Upgrade Header", "WebSocket Handshake"],
                    authentication_required=False,
                    max_connections=1000,
                    heartbeat_interval=30
                )
            ],
            failover_mechanisms=[
                FailoverMechanism(
                    mechanism_id="dns_failover_001",
                    failover_type=FailoverType.DNS_FAILOVER,
                    description="DNS-based failover for domain resolution",
                    primary_target="Cloudflare DNS",
                    fallback_targets=["Direct IP access"],
                    detection_method="DNS resolution timeout",
                    failover_time="30s",
                    recovery_time="60s",
                    health_check_interval="10s",
                    max_retries=3,
                    auto_recovery=True
                )
            ],
            discovery_timestamp=datetime.now()
        )
    
    def test_initialization(self, discoverer):
        """Test NetworkTopologyDiscoverer initialization."""
        assert discoverer.module_id == "NetworkTopologyDiscoverer"
        assert discoverer._scan_timeout == 1.0
        assert discoverer._max_concurrent_scans == 5
        assert discoverer._tunnel_id == "d1e53e43-033f-4994-8f46-c83962ae3785"
        assert discoverer._primary_domain == "observatory.nkllon.com"
        assert len(discoverer._subdomains) == 2
        assert len(discoverer._websocket_endpoints) == 4
        assert discoverer._topology is None
        assert discoverer._discovery_errors == []
    
    def test_get_module_info(self, discoverer):
        """Test get_module_info method."""
        info = discoverer.get_module_info()
        
        assert info["module_id"] == "NetworkTopologyDiscoverer"
        assert info["name"] == "NetworkTopologyDiscoverer"
        assert info["version"] == "1.0.0"
        assert info["description"] == "Comprehensive network topology discovery for Beast Mode framework"
        assert info["task"] == "1.6 - Network Topology Discovery"
        assert info["specification"] == "system-architecture-wiring-diagram"
        assert "capabilities" in info
    
    def test_get_capabilities(self, discoverer):
        """Test get_capabilities method."""
        capabilities = discoverer.get_capabilities()
        
        assert len(capabilities) == 4
        assert "CORE_FUNCTIONALITY" in [cap.value for cap in capabilities]
        assert "DATA_PROCESSING" in [cap.value for cap in capabilities]
        assert "VALIDATION" in [cap.value for cap in capabilities]
        assert "MONITORING" in [cap.value for cap in capabilities]
    
    @patch('socket.socket')
    def test_get_health_status_healthy(self, mock_socket, discoverer):
        """Test get_health_status when module is healthy."""
        # Mock socket creation and closing
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        
        # Set topology with recent data
        discoverer._topology = Mock()
        discoverer._topology.discovery_timestamp = datetime.now()
        discoverer._discovery_errors = []
        
        health = discoverer.get_health_status()
        
        assert health.status.value == "healthy"
        assert health.health_score == 1.0
        assert len(health.issues) == 0
        assert health.module_id == "NetworkTopologyDiscoverer"
    
    @patch('socket.socket')
    def test_get_health_status_warning(self, mock_socket, discoverer):
        """Test get_health_status when module has warnings."""
        # Mock socket creation and closing
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        
        # Set topology with recent data but some errors
        discoverer._topology = Mock()
        discoverer._topology.discovery_timestamp = datetime.now()
        discoverer._discovery_errors = ["DNS resolution failed", "Port scan timeout"]
        
        health = discoverer.get_health_status()
        
        assert health.status.value == "warning"
        assert health.health_score == 0.8
        assert len(health.issues) == 2
        assert "DNS resolution failed" in health.issues
    
    @patch('socket.socket')
    def test_get_health_status_error(self, mock_socket, discoverer):
        """Test get_health_status when module has errors."""
        # Mock socket creation and closing
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        
        # Set topology with old data and many errors
        discoverer._topology = Mock()
        discoverer._topology.discovery_timestamp = datetime(2020, 1, 1)
        discoverer._discovery_errors = ["Error 1", "Error 2", "Error 3", "Error 4"]
        
        health = discoverer.get_health_status()
        
        assert health.status.value == "error"
        assert health.health_score == 0.3
        assert len(health.issues) == 3  # Only first 3 errors shown
    
    @patch('socket.socket')
    def test_get_health_status_socket_error(self, mock_socket, discoverer):
        """Test get_health_status when socket operations fail."""
        # Mock socket to raise exception
        mock_socket.side_effect = Exception("Socket error")
        
        health = discoverer.get_health_status()
        
        assert health.status.value == "error"
        assert health.health_score == 0.0
        assert "Socket error" in health.issues[0]
    
    def test_graceful_degradation(self, discoverer):
        """Test graceful degradation functionality."""
        result = discoverer.graceful_degradation()
        
        assert isinstance(result.success, bool)
        assert isinstance(result.degraded_capabilities, list)
        assert isinstance(result.remaining_capabilities, list)
        assert result.error_message is None or isinstance(result.error_message, str)
    
    @patch('socket.gethostname')
    @patch('socket.gethostbyname')
    def test_discover_local_network_range(self, mock_gethostbyname, mock_gethostname, discoverer):
        """Test local network range discovery."""
        mock_gethostname.return_value = "test-host"
        mock_gethostbyname.return_value = "192.168.1.100"
        
        network_range = discoverer._discover_local_network_range()
        
        assert network_range == "192.168.1.x"
        mock_gethostname.assert_called_once()
        mock_gethostbyname.assert_called_once_with("test-host")
    
    @patch('socket.gethostname')
    @patch('socket.gethostbyname')
    def test_discover_local_network_range_10_net(self, mock_gethostbyname, mock_gethostname, discoverer):
        """Test local network range discovery for 10.x.x.x network."""
        mock_gethostname.return_value = "test-host"
        mock_gethostbyname.return_value = "10.0.0.100"
        
        network_range = discoverer._discover_local_network_range()
        
        assert network_range == "10.x.x.x"
    
    @patch('socket.gethostname')
    @patch('socket.gethostbyname')
    def test_discover_local_network_range_172_net(self, mock_gethostbyname, mock_gethostname, discoverer):
        """Test local network range discovery for 172.16-31.x.x network."""
        mock_gethostname.return_value = "test-host"
        mock_gethostbyname.return_value = "172.16.0.100"
        
        network_range = discoverer._discover_local_network_range()
        
        assert network_range == "172.16-31.x.x"
    
    @patch('socket.gethostname')
    @patch('socket.gethostbyname')
    def test_discover_local_network_range_other(self, mock_gethostbyname, mock_gethostname, discoverer):
        """Test local network range discovery for other networks."""
        mock_gethostname.return_value = "test-host"
        mock_gethostbyname.return_value = "203.0.113.100"
        
        network_range = discoverer._discover_local_network_range()
        
        assert network_range == "203.0.113.100/24"
    
    @patch('socket.gethostname')
    @patch('socket.gethostbyname')
    def test_discover_local_network_range_error(self, mock_gethostbyname, mock_gethostname, discoverer):
        """Test local network range discovery with error."""
        mock_gethostname.side_effect = Exception("Hostname error")
        
        network_range = discoverer._discover_local_network_range()
        
        assert network_range == "192.168.1.x"  # Default fallback
    
    @patch('src.system_architecture.discovery.network_topology_discoverer.ThreadPoolExecutor')
    @patch.object(discoverer, '_scan_service_endpoint')
    @patch.object(discoverer, '_discover_additional_services')
    def test_discover_service_endpoints(self, mock_additional, mock_scan, mock_executor, discoverer):
        """Test service endpoint discovery."""
        # Mock executor and futures
        mock_future = Mock()
        mock_future.result.return_value = ServiceEndpoint(
            name="Observatory Server",
            host="localhost",
            port=8888,
            protocol=Protocol.TCP,
            status=ServiceStatus.ACTIVE,
            last_checked=datetime.now()
        )
        
        mock_executor_instance = Mock()
        mock_executor_instance.__enter__.return_value = mock_executor_instance
        mock_executor_instance.submit.return_value = mock_future
        mock_executor_instance.__exit__.return_value = None
        mock_executor.return_value = mock_executor_instance
        
        # Mock additional services
        mock_additional.return_value = []
        
        endpoints = discoverer._discover_service_endpoints()
        
        assert len(endpoints) == 1
        assert endpoints[0].name == "Observatory Server"
        assert endpoints[0].port == 8888
        mock_executor.assert_called_once()
        mock_additional.assert_called_once()
    
    @patch.object(discoverer, '_is_port_open')
    @patch('requests.get')
    def test_scan_service_endpoint_active(self, mock_get, mock_port_open, discoverer):
        """Test scanning an active service endpoint."""
        mock_port_open.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        endpoint = discoverer._scan_service_endpoint(8888, "Observatory Server")
        
        assert endpoint is not None
        assert endpoint.name == "Observatory Server"
        assert endpoint.port == 8888
        assert endpoint.protocol == Protocol.TCP
        assert endpoint.status == ServiceStatus.ACTIVE
        assert endpoint.response_time_ms is not None
        assert endpoint.health_endpoint == "/health"
        assert len(endpoint.websocket_endpoints) > 0
    
    @patch.object(discoverer, '_is_port_open')
    def test_scan_service_endpoint_port_closed(self, mock_port_open, discoverer):
        """Test scanning a closed service endpoint."""
        mock_port_open.return_value = False
        
        endpoint = discoverer._scan_service_endpoint(8888, "Observatory Server")
        
        assert endpoint is None
    
    @patch.object(discoverer, '_is_port_open')
    @patch('requests.get')
    def test_scan_service_endpoint_request_error(self, mock_get, mock_port_open, discoverer):
        """Test scanning service endpoint with request error."""
        mock_port_open.return_value = True
        mock_get.side_effect = Exception("Request error")
        
        endpoint = discoverer._scan_service_endpoint(8888, "Observatory Server")
        
        assert endpoint is not None
        assert endpoint.status == ServiceStatus.UNKNOWN
        assert endpoint.response_time_ms is None
    
    @patch.object(discoverer, '_is_port_open')
    def test_discover_additional_services(self, mock_port_open, discoverer):
        """Test discovery of additional services."""
        mock_port_open.return_value = True
        
        endpoints = discoverer._discover_additional_services()
        
        assert len(endpoints) > 0
        assert all(ep.protocol == Protocol.TCP for ep in endpoints)
        assert all(ep.status == ServiceStatus.ACTIVE for ep in endpoints)
    
    def test_discover_network_flows(self, discoverer):
        """Test network flow discovery."""
        endpoints = [
            ServiceEndpoint(
                name="Observatory Server",
                host="localhost",
                port=8888,
                protocol=Protocol.TCP,
                status=ServiceStatus.ACTIVE,
                last_checked=datetime.now()
            ),
            ServiceEndpoint(
                name="Prometheus",
                host="localhost",
                port=9090,
                protocol=Protocol.TCP,
                status=ServiceStatus.ACTIVE,
                last_checked=datetime.now()
            )
        ]
        
        flows = discoverer._discover_network_flows(endpoints)
        
        assert len(flows) >= 4  # Internet flow + 3 internal flows + Redis flow
        assert any(flow.source == "Internet" for flow in flows)
        assert any(flow.destination == "Cloudflare Edge" for flow in flows)
        assert any(flow.protocol == Protocol.HTTPS for flow in flows)
        assert any(flow.flow_type == FlowType.INGRESS for flow in flows)
        assert any(flow.protocol == Protocol.REDIS for flow in flows)
    
    @patch('socket.gethostbyname')
    def test_discover_dns_mappings(self, mock_gethostbyname, discoverer):
        """Test DNS mapping discovery."""
        mock_gethostbyname.return_value = "203.0.113.1"
        
        mappings = discoverer._discover_dns_mappings()
        
        assert len(mappings) == 3
        assert any(mapping.domain == "observatory.nkllon.com" for mapping in mappings)
        assert any(mapping.domain == "grafana.observatory.nkllon.com" for mapping in mappings)
        assert any(mapping.domain == "prometheus.observatory.nkllon.com" for mapping in mappings)
        assert all(mapping.tunnel_id == "d1e53e43-033f-4994-8f46-c83962ae3785" for mapping in mappings)
        assert all(mapping.ttl_seconds == 300 for mapping in mappings)
    
    @patch('socket.gethostbyname')
    def test_discover_dns_mappings_resolution_error(self, mock_gethostbyname, discoverer):
        """Test DNS mapping discovery with resolution error."""
        mock_gethostbyname.side_effect = socket.gaierror("Name resolution failed")
        
        mappings = discoverer._discover_dns_mappings()
        
        assert len(mappings) == 3
        assert all("dns-resolution-failed" in mapping.failover_targets for mapping in mappings)
    
    @patch.object(discoverer, '_is_port_open')
    def test_discover_redis_coordination_healthy(self, mock_port_open, discoverer):
        """Test Redis coordination discovery when healthy."""
        def port_check(host, port):
            if host == "192.168.1.119" and port == 6379:
                return True
            elif host == "localhost" and port == 6380:
                return True
            return False
        
        mock_port_open.side_effect = port_check
        
        redis_config = discoverer._discover_redis_coordination()
        
        assert redis_config is not None
        assert redis_config.primary_endpoint == "192.168.1.119:6379"
        assert redis_config.health_status == "healthy"
        assert "localhost:6380" in redis_config.fallback_endpoints
        assert redis_config.cluster_mode is False
        assert redis_config.automatic_failover is True
    
    @patch.object(discoverer, '_is_port_open')
    def test_discover_redis_coordination_degraded(self, mock_port_open, discoverer):
        """Test Redis coordination discovery when degraded."""
        def port_check(host, port):
            if host == "192.168.1.119" and port == 6379:
                return False  # Primary down
            elif host == "localhost" and port == 6380:
                return True   # Fallback up
            return False
        
        mock_port_open.side_effect = port_check
        
        redis_config = discoverer._discover_redis_coordination()
        
        assert redis_config is not None
        assert redis_config.health_status == "degraded"
        assert "localhost:6380" in redis_config.fallback_endpoints
    
    @patch.object(discoverer, '_is_port_open')
    def test_discover_redis_coordination_unhealthy(self, mock_port_open, discoverer):
        """Test Redis coordination discovery when unhealthy."""
        mock_port_open.return_value = False  # All endpoints down
        
        redis_config = discoverer._discover_redis_coordination()
        
        assert redis_config is not None
        assert redis_config.health_status == "unhealthy"
        assert len(redis_config.fallback_endpoints) == 0
    
    def test_discover_websocket_configurations(self, discoverer):
        """Test WebSocket configuration discovery."""
        configs = discoverer._discover_websocket_configurations()
        
        assert len(configs) == 4
        assert any(config.endpoint == "/ws/observatory" for config in configs)
        assert any(config.endpoint == "/ws/emoji-rain" for config in configs)
        assert any(config.endpoint == "/ws/anomalies" for config in configs)
        assert any(config.endpoint == "/ws/doctor-status" for config in configs)
        
        for config in configs:
            assert "websocket" in config.supported_protocols
            assert len(config.connection_flow) > 0
            assert config.max_connections == 1000
            assert config.heartbeat_interval == 30
    
    def test_map_port_allocations(self, discoverer):
        """Test port allocation mapping."""
        endpoints = [
            ServiceEndpoint(
                name="Test Service",
                host="localhost",
                port=8080,
                protocol=Protocol.TCP,
                status=ServiceStatus.ACTIVE,
                last_checked=datetime.now()
            )
        ]
        
        allocations = discoverer._map_port_allocations(endpoints)
        
        assert allocations[8080] == "Test Service"
        assert allocations[8888] == "Observatory Server"  # From known ports
        assert allocations[9090] == "Prometheus"  # From known ports
    
    def test_discover_routing_configurations(self, discoverer):
        """Test routing configuration discovery."""
        configs = discoverer._discover_routing_configurations()
        
        assert len(configs) == 2
        assert any(config["type"] == "cloudflare_tunnel" for config in configs)
        assert any(config["type"] == "internal_routing" for config in configs)
        
        tunnel_config = next(config for config in configs if config["type"] == "cloudflare_tunnel")
        assert tunnel_config["tunnel_id"] == "d1e53e43-033f-4994-8f46-c83962ae3785"
        assert len(tunnel_config["ingress_rules"]) == 3
    
    def test_discover_failover_mechanisms(self, discoverer):
        """Test failover mechanism discovery."""
        mechanisms = discoverer._discover_failover_mechanisms()
        
        assert len(mechanisms) == 4
        assert any(mech.failover_type == FailoverType.DNS_FAILOVER for mech in mechanisms)
        assert any(mech.failover_type == FailoverType.REDIS_FAILOVER for mech in mechanisms)
        assert any(mech.failover_type == FailoverType.WEBSOCKET_FAILOVER for mech in mechanisms)
        assert any(mech.failover_type == FailoverType.SERVICE_FAILOVER for mech in mechanisms)
        
        for mechanism in mechanisms:
            assert mechanism.mechanism_id is not None
            assert mechanism.description is not None
            assert mechanism.primary_target is not None
            assert len(mechanism.fallback_targets) > 0
            assert mechanism.auto_recovery is True
            assert mechanism.max_retries == 3
    
    def test_is_port_open(self, discoverer):
        """Test port open checking."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.connect_ex.return_value = 0  # Success
            mock_socket.return_value.__enter__.return_value = mock_sock
            
            result = discoverer._is_port_open("localhost", 8888)
            
            assert result is True
            mock_sock.connect_ex.assert_called_once_with(("localhost", 8888))
    
    def test_is_port_open_closed(self, discoverer):
        """Test port open checking for closed port."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.connect_ex.return_value = 1  # Connection refused
            mock_socket.return_value.__enter__.return_value = mock_sock
            
            result = discoverer._is_port_open("localhost", 9999)
            
            assert result is False
    
    def test_is_port_open_timeout(self, discoverer):
        """Test port open checking with timeout."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.connect_ex.side_effect = Exception("Timeout")
            mock_socket.return_value.__enter__.return_value = mock_sock
            
            result = discoverer._is_port_open("localhost", 8888)
            
            assert result is False
    
    def test_get_health_endpoint(self, discoverer):
        """Test health endpoint retrieval."""
        assert discoverer._get_health_endpoint("Observatory Server", 8888) == "/health"
        assert discoverer._get_health_endpoint("Prometheus", 9090) == "/metrics"
        assert discoverer._get_health_endpoint("Grafana", 3000) == "/api/health"
        assert discoverer._get_health_endpoint("Redis Primary", 6379) is None
        assert discoverer._get_health_endpoint("Directus CMS", 8055) == "/server/ping"
        assert discoverer._get_health_endpoint("Unknown Service", 9999) is None
    
    def test_get_websocket_endpoints(self, discoverer):
        """Test WebSocket endpoint retrieval."""
        endpoints = discoverer._get_websocket_endpoints("Observatory Server", 8888)
        
        assert len(endpoints) == 4
        assert "/ws/observatory" in endpoints
        assert "/ws/emoji-rain" in endpoints
        assert "/ws/anomalies" in endpoints
        assert "/ws/doctor-status" in endpoints
        
        # Test other services
        assert discoverer._get_websocket_endpoints("Prometheus", 9090) == []
        assert discoverer._get_websocket_endpoints("Grafana", 3000) == []
    
    @patch.object(discoverer, '_discover_local_network_range')
    @patch.object(discoverer, '_discover_service_endpoints')
    @patch.object(discoverer, '_discover_network_flows')
    @patch.object(discoverer, '_discover_dns_mappings')
    @patch.object(discoverer, '_discover_redis_coordination')
    @patch.object(discoverer, '_discover_websocket_configurations')
    @patch.object(discoverer, '_map_port_allocations')
    @patch.object(discoverer, '_discover_routing_configurations')
    @patch.object(discoverer, '_discover_failover_mechanisms')
    def test_discover_network_topology_success(self, mock_failover, mock_routing, mock_ports, 
                                               mock_websocket, mock_redis, mock_dns, 
                                               mock_flows, mock_endpoints, mock_network, discoverer):
        """Test successful network topology discovery."""
        # Mock all discovery methods
        mock_network.return_value = "192.168.1.x"
        mock_endpoints.return_value = [Mock()]
        mock_flows.return_value = [Mock()]
        mock_dns.return_value = [Mock()]
        mock_redis.return_value = Mock()
        mock_websocket.return_value = [Mock()]
        mock_ports.return_value = {8888: "Observatory Server"}
        mock_routing.return_value = [Mock()]
        mock_failover.return_value = [Mock()]
        
        topology = discoverer.discover_network_topology()
        
        assert isinstance(topology, NetworkTopology)
        assert topology.local_network_range == "192.168.1.x"
        assert discoverer._topology == topology
        assert len(discoverer._discovery_errors) == 0
    
    @patch.object(discoverer, '_discover_local_network_range')
    def test_discover_network_topology_error(self, mock_network, discoverer):
        """Test network topology discovery with error."""
        mock_network.side_effect = Exception("Discovery error")
        
        with pytest.raises(Exception, match="Discovery error"):
            discoverer.discover_network_topology()
        
        assert "Discovery error" in discoverer._discovery_errors
    
    def test_generate_network_diagram(self, discoverer, mock_topology):
        """Test network diagram generation."""
        discoverer._topology = mock_topology
        
        diagram = discoverer.generate_network_diagram()
        
        assert isinstance(diagram, dict)
        assert "nodes" in diagram
        assert "edges" in diagram
        assert "metadata" in diagram
        assert len(diagram["nodes"]) > 0
        assert len(diagram["edges"]) > 0
    
    def test_generate_network_diagram_no_topology(self, discoverer):
        """Test network diagram generation without topology."""
        with patch.object(discoverer, 'discover_network_topology') as mock_discover:
            mock_discover.return_value = Mock()
            
            diagram = discoverer.generate_network_diagram()
            
            assert isinstance(diagram, dict)
            mock_discover.assert_called_once()
    
    def test_export_topology_json(self, discoverer, mock_topology):
        """Test topology export to JSON."""
        discoverer._topology = mock_topology
        
        json_data = discoverer.export_topology_json()
        
        assert isinstance(json_data, str)
        parsed = json.loads(json_data)
        assert "local_network_range" in parsed
        assert "service_endpoints" in parsed
        assert "network_flows" in parsed
    
    def test_export_topology_yaml(self, discoverer, mock_topology):
        """Test topology export to YAML."""
        discoverer._topology = mock_topology
        
        yaml_data = discoverer.export_topology_yaml()
        
        assert isinstance(yaml_data, str)
        assert "local_network_range:" in yaml_data
        assert "service_endpoints:" in yaml_data
    
    def test_export_topology_to_file(self, discoverer, mock_topology, tmp_path):
        """Test topology export to file."""
        discoverer._topology = mock_topology
        file_path = tmp_path / "topology.json"
        
        discoverer.export_topology_to_file(str(file_path))
        
        assert file_path.exists()
        with open(file_path) as f:
            data = json.load(f)
        assert "local_network_range" in data
    
    def test_validate_topology(self, discoverer, mock_topology):
        """Test topology validation."""
        discoverer._topology = mock_topology
        
        issues = discoverer.validate_topology()
        
        assert isinstance(issues, list)
        # Should have no issues with valid topology
        assert len(issues) == 0
    
    def test_get_topology_summary(self, discoverer, mock_topology):
        """Test topology summary generation."""
        discoverer._topology = mock_topology
        
        summary = discoverer.get_topology_summary()
        
        assert isinstance(summary, dict)
        assert "discovery_timestamp" in summary
        assert "topology_version" in summary
        assert "network_range" in summary
        assert "total_services" in summary
        assert "active_services" in summary
        assert "total_flows" in summary
        assert "dns_mappings" in summary
        assert "websocket_endpoints" in summary
        assert "redis_configured" in summary
        assert "failover_mechanisms" in summary
        assert "port_allocations" in summary
        assert "validation_issues" in summary


class TestNetworkTopologyDiscovererIntegration:
    """Integration tests for NetworkTopologyDiscoverer."""
    
    @pytest.fixture
    def discoverer(self):
        """Create NetworkTopologyDiscoverer instance for integration testing."""
        return NetworkTopologyDiscoverer()
    
    def test_full_discovery_workflow(self, discoverer):
        """Test complete discovery workflow."""
        # This test will use real network operations where possible
        # but will mock external dependencies
        
        with patch('socket.gethostname') as mock_hostname, \
             patch('socket.gethostbyname') as mock_hostbyname, \
             patch.object(discoverer, '_is_port_open') as mock_port_open, \
             patch('requests.get') as mock_get:
            
            # Mock network operations
            mock_hostname.return_value = "test-host"
            mock_hostbyname.return_value = "192.168.1.100"
            mock_port_open.return_value = True
            mock_get.return_value = Mock(status_code=200)
            
            topology = discoverer.discover_network_topology()
            
            assert isinstance(topology, NetworkTopology)
            assert topology.local_network_range == "192.168.1.x"
            assert len(topology.service_endpoints) > 0
            assert len(topology.network_flows) > 0
            assert len(topology.dns_mappings) > 0
            assert topology.redis_coordination is not None
            assert len(topology.websocket_configs) > 0
            assert len(topology.failover_mechanisms) > 0
    
    def test_error_handling_and_recovery(self, discoverer):
        """Test error handling and recovery mechanisms."""
        # Test with various error conditions
        with patch.object(discoverer, '_discover_local_network_range') as mock_network, \
             patch.object(discoverer, '_discover_service_endpoints') as mock_endpoints:
            
            mock_network.side_effect = Exception("Network error")
            mock_endpoints.side_effect = Exception("Service error")
            
            with pytest.raises(Exception):
                discoverer.discover_network_topology()
            
            assert len(discoverer._discovery_errors) > 0
            assert any("Network error" in error for error in discoverer._discovery_errors)
            assert any("Service error" in error for error in discoverer._discovery_errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.system_architecture.discovery.network_topology_discoverer", "--cov-report=html"])