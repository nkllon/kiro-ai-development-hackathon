#!/usr/bin/env python3
"""
Comprehensive Unit Tests for CloudflareTunnelDiscoverer

Tests the CloudflareTunnelDiscoverer implementation with >90% coverage
as required by Task 1.4 of the System Architecture Wiring Diagram spec.
"""

import pytest
import tempfile
import os
import json
import yaml
import subprocess
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

from src.system_architecture.discovery.cloudflare_tunnel_discoverer import (
    CloudflareTunnelDiscoverer,
    TunnelIngressRule,
    DNSRouting,
    TunnelConfiguration,
    WebSocketConnectivityTest
)
from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleCapability


class TestCloudflareTunnelDiscoverer:
    """Test suite for CloudflareTunnelDiscoverer"""

    @pytest.fixture
    def discoverer(self):
        """Create a CloudflareTunnelDiscoverer instance for testing"""
        return CloudflareTunnelDiscoverer()

    @pytest.fixture
    def mock_config_file(self):
        """Create a mock tunnel configuration file"""
        config = {
            'tunnel': 'd1e53e43-033f-4994-8f46-c83962ae3785',
            'credentials-file': '/Users/lou/.cloudflared/d1e53e43-033f-4994-8f46-c83962ae3785.json',
            'ingress': [
                {
                    'hostname': 'observatory.nkllon.com',
                    'service': 'http://localhost:8888',
                    'originRequest': {
                        'httpHostHeader': 'localhost:8888',
                        'noTLSVerify': False,
                        'connectTimeout': '30s'
                    }
                },
                {
                    'hostname': 'grafana.observatory.nkllon.com',
                    'service': 'http://localhost:3000'
                },
                {
                    'hostname': 'prometheus.observatory.nkllon.com',
                    'service': 'http://localhost:9090'
                },
                {
                    'service': 'http_status:404'
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config, f)
            yield f.name
        
        os.unlink(f.name)

    @pytest.fixture
    def mock_credentials_file(self):
        """Create a mock credentials file"""
        credentials = {
            'AccountTag': 'test-account',
            'TunnelSecret': 'test-secret'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials, f)
            yield f.name
        
        os.unlink(f.name)

    def test_initialization(self, discoverer):
        """Test CloudflareTunnelDiscoverer initialization"""
        assert discoverer.module_id == "cloudflare_tunnel_discoverer"
        assert discoverer.expected_tunnel_id == "d1e53e43-033f-4994-8f46-c83962ae3785"
        assert len(discoverer.expected_subdomains) == 3
        assert "observatory.nkllon.com" in discoverer.expected_subdomains
        assert discoverer._tunnel_config is None
        assert discoverer._last_discovery_time is None
        assert discoverer._discovery_errors == []

    def test_get_module_info(self, discoverer):
        """Test get_module_info method"""
        info = discoverer.get_module_info()
        
        assert info["module_id"] == "cloudflare_tunnel_discoverer"
        assert info["name"] == "Cloudflare Tunnel Discoverer"
        assert info["version"] == "1.0.0"
        assert info["expected_tunnel_id"] == "d1e53e43-033f-4994-8f46-c83962ae3785"
        assert len(info["expected_subdomains"]) == 3
        assert info["discovery_errors"] == 0
        assert info["tunnel_status"] == "unknown"

    def test_get_capabilities(self, discoverer):
        """Test get_capabilities method"""
        capabilities = discoverer.get_capabilities()
        
        expected_capabilities = [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
        
        assert capabilities == expected_capabilities

    def test_get_health_status_healthy(self, discoverer):
        """Test get_health_status when healthy"""
        health = discoverer.get_health_status()
        
        assert health.module_id == "cloudflare_tunnel_discoverer"
        assert health.status == ModuleStatus.HEALTHY
        assert health.health_score == 1.0
        assert health.issues == []
        assert health.error_count == 0
        assert health.warning_count == 0

    def test_get_health_status_with_errors(self, discoverer):
        """Test get_health_status with discovery errors"""
        discoverer._discovery_errors = ["Test error 1", "Test error 2"]
        
        health = discoverer.get_health_status()
        
        assert health.status == ModuleStatus.WARNING
        assert health.health_score == 0.7
        assert len(health.issues) == 2

    def test_get_health_status_no_tunnel_config(self, discoverer):
        """Test get_health_status when no tunnel config"""
        discoverer._tunnel_config = None
        
        health = discoverer.get_health_status()
        
        assert health.status == ModuleStatus.ERROR
        assert health.health_score == 0.3
        assert "No tunnel configuration discovered" in health.issues

    def test_get_health_status_inactive_tunnel(self, discoverer):
        """Test get_health_status when tunnel is inactive"""
        discoverer._tunnel_config = Mock()
        discoverer._tunnel_config.status = "inactive"
        
        health = discoverer.get_health_status()
        
        assert health.status == ModuleStatus.WARNING
        assert health.health_score == 0.6
        assert "Tunnel status: inactive" in health.issues

    def test_graceful_degradation_success(self, discoverer):
        """Test graceful degradation success"""
        result = discoverer.graceful_degradation()
        
        assert result.success is True
        assert ModuleCapability.MONITORING in result.remaining_capabilities
        assert ModuleCapability.CORE_FUNCTIONALITY in result.degraded_capabilities

    def test_graceful_degradation_failure(self, discoverer):
        """Test graceful degradation failure"""
        with patch.object(discoverer.logger, 'warning', side_effect=Exception("Test error")):
            result = discoverer.graceful_degradation()
            
            assert result.success is False
            assert result.error_message == "Test error"

    @patch('os.path.exists')
    def test_find_tunnel_config_file_success(self, mock_exists, discoverer):
        """Test finding tunnel config file successfully"""
        mock_exists.return_value = True
        
        config_file = discoverer._find_tunnel_config_file()
        
        assert config_file is not None
        mock_exists.assert_called()

    @patch('os.path.exists')
    def test_find_tunnel_config_file_not_found(self, mock_exists, discoverer):
        """Test when tunnel config file is not found"""
        mock_exists.return_value = False
        
        config_file = discoverer._find_tunnel_config_file()
        
        assert config_file is None

    def test_find_tunnel_credentials_success(self, discoverer):
        """Test finding tunnel credentials successfully"""
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'glob', return_value=[Path('/test/credentials.json')]):
            
            credentials_file = discoverer._find_tunnel_credentials()
            
            assert credentials_file == '/test/credentials.json'

    def test_find_tunnel_credentials_not_found(self, discoverer):
        """Test when tunnel credentials are not found"""
        with patch.object(Path, 'exists', return_value=False):
            credentials_file = discoverer._find_tunnel_credentials()
            
            assert credentials_file is None

    def test_parse_ingress_rules_success(self, discoverer, mock_config_file):
        """Test parsing ingress rules successfully"""
        rules = discoverer._parse_ingress_rules(mock_config_file)
        
        assert len(rules) == 4
        assert rules[0].hostname == "observatory.nkllon.com"
        assert rules[0].service == "http://localhost:8888"
        assert rules[3].hostname is None  # Catch-all rule

    def test_parse_ingress_rules_no_file(self, discoverer):
        """Test parsing ingress rules when no file exists"""
        rules = discoverer._parse_ingress_rules(None)
        
        assert len(rules) == 4  # Default rules
        assert rules[0].hostname == "observatory.nkllon.com"

    def test_parse_ingress_rules_invalid_file(self, discoverer):
        """Test parsing ingress rules with invalid file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            
            rules = discoverer._parse_ingress_rules(f.name)
            
            assert len(rules) == 4  # Default rules
        
        os.unlink(f.name)

    def test_create_default_ingress_rules(self, discoverer):
        """Test creating default ingress rules"""
        rules = discoverer._create_default_ingress_rules()
        
        assert len(rules) == 4
        assert rules[0].hostname == "observatory.nkllon.com"
        assert rules[1].hostname == "grafana.observatory.nkllon.com"
        assert rules[2].hostname == "prometheus.observatory.nkllon.com"
        assert rules[3].hostname is None  # Catch-all

    def test_map_dns_routing(self, discoverer):
        """Test mapping DNS routing"""
        routing = discoverer._map_dns_routing()
        
        assert len(routing) == 3
        assert routing[0].subdomain == "observatory.nkllon.com"
        assert routing[0].target_service == "Observatory"
        assert routing[0].port == 8888
        assert routing[0].websocket_enabled is True
        assert routing[1].websocket_enabled is False

    @patch('subprocess.run')
    def test_check_tunnel_status_active(self, mock_run, discoverer):
        """Test checking tunnel status when active"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "12345\n"
        
        status = discoverer._check_tunnel_status()
        
        assert status == "active"
        mock_run.assert_called_with(
            ["pgrep", "-f", "cloudflared"],
            capture_output=True,
            text=True,
            timeout=10
        )

    @patch('subprocess.run')
    def test_check_tunnel_status_inactive(self, mock_run, discoverer):
        """Test checking tunnel status when inactive"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        
        status = discoverer._check_tunnel_status()
        
        assert status == "inactive"

    @patch('subprocess.run')
    def test_check_tunnel_status_timeout(self, mock_run, discoverer):
        """Test checking tunnel status with timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired("pgrep", 10)
        
        status = discoverer._check_tunnel_status()
        
        assert status == "unknown"

    @patch('subprocess.run')
    def test_check_tunnel_status_error(self, mock_run, discoverer):
        """Test checking tunnel status with error"""
        mock_run.side_effect = Exception("Test error")
        
        status = discoverer._check_tunnel_status()
        
        assert status == "error"

    def test_discover_tunnel_configuration_success(self, discoverer, mock_config_file, mock_credentials_file):
        """Test successful tunnel configuration discovery"""
        with patch.object(discoverer, '_find_tunnel_config_file', return_value=mock_config_file), \
             patch.object(discoverer, '_find_tunnel_credentials', return_value=mock_credentials_file), \
             patch.object(discoverer, '_check_tunnel_status', return_value="active"):
            
            config = discoverer.discover_tunnel_configuration()
            
            assert config.tunnel_id == "d1e53e43-033f-4994-8f46-c83962ae3785"
            assert config.tunnel_name == "observatory-tunnel"
            assert config.status == "active"
            assert len(config.ingress_rules) == 4
            assert len(config.dns_routing) == 3

    def test_discover_tunnel_configuration_failure(self, discoverer):
        """Test tunnel configuration discovery failure"""
        with patch.object(discoverer, '_find_tunnel_config_file', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                discoverer.discover_tunnel_configuration()
            
            assert len(discoverer._discovery_errors) == 1

    @patch('requests.get')
    def test_validate_subdomain_routing_success(self, mock_get, discoverer):
        """Test successful subdomain routing validation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        with patch('time.time', side_effect=[0, 0.1]):
            results = discoverer.validate_subdomain_routing()
            
            assert len(results) == 3
            assert results["observatory.nkllon.com"]["accessible"] is True
            assert results["observatory.nkllon.com"]["ssl_valid"] is True
            assert results["observatory.nkllon.com"]["response_time_ms"] == 100.0

    @patch('requests.get')
    def test_validate_subdomain_routing_ssl_error(self, mock_get, discoverer):
        """Test subdomain routing validation with SSL error"""
        mock_get.side_effect = requests.exceptions.SSLError("SSL Error")
        
        results = discoverer.validate_subdomain_routing()
        
        assert results["observatory.nkllon.com"]["accessible"] is False
        assert results["observatory.nkllon.com"]["ssl_valid"] is False
        assert "SSL validation failed" in results["observatory.nkllon.com"]["error"]

    @patch('requests.get')
    def test_validate_subdomain_routing_request_error(self, mock_get, discoverer):
        """Test subdomain routing validation with request error"""
        mock_get.side_effect = requests.exceptions.RequestException("Request Error")
        
        results = discoverer.validate_subdomain_routing()
        
        assert results["observatory.nkllon.com"]["accessible"] is False
        assert "Request failed" in results["observatory.nkllon.com"]["error"]

    @patch('requests.get')
    def test_test_websocket_connectivity_success(self, mock_get, discoverer):
        """Test successful WebSocket connectivity test"""
        mock_response = Mock()
        mock_response.status_code = 426  # Upgrade Required
        mock_get.return_value = mock_response
        
        with patch('time.time', side_effect=[0, 0.05]):
            results = discoverer.test_websocket_connectivity()
            
            assert len(results) == 4
            assert results[0].accessible is True
            assert results[0].upgrade_successful is True
            assert results[0].response_time_ms == 50.0

    @patch('requests.get')
    def test_test_websocket_connectivity_failure(self, mock_get, discoverer):
        """Test WebSocket connectivity test failure"""
        mock_get.side_effect = Exception("Connection Error")
        
        results = discoverer.test_websocket_connectivity()
        
        assert len(results) == 4
        assert results[0].accessible is False
        assert results[0].error_message == "Connection Error"

    def test_get_tunnel_performance_metrics(self, discoverer):
        """Test getting tunnel performance metrics"""
        with patch.object(discoverer, 'validate_subdomain_routing') as mock_validate:
            mock_validate.return_value = {
                "observatory.nkllon.com": {
                    "accessible": True,
                    "response_time_ms": 100.0,
                    "ssl_valid": True
                },
                "grafana.observatory.nkllon.com": {
                    "accessible": False,
                    "response_time_ms": None,
                    "ssl_valid": False
                }
            }
            
            metrics = discoverer.get_tunnel_performance_metrics()
            
            assert metrics["tunnel_id"] == "d1e53e43-033f-4994-8f46-c83962ae3785"
            assert "connectivity_tests" in metrics
            assert "performance_summary" in metrics
            assert metrics["performance_summary"]["accessibility_rate"] == 0.5

    def test_get_tunnel_performance_metrics_error(self, discoverer):
        """Test getting tunnel performance metrics with error"""
        with patch.object(discoverer, 'validate_subdomain_routing', side_effect=Exception("Test error")):
            metrics = discoverer.get_tunnel_performance_metrics()
            
            assert "error" in metrics
            assert metrics["error"] == "Test error"

    def test_generate_tunnel_report_success(self, discoverer):
        """Test generating tunnel report successfully"""
        mock_config = Mock()
        mock_config.tunnel_id = "test-tunnel"
        mock_config.tunnel_name = "test-tunnel"
        mock_config.status = "active"
        mock_config.config_file = "test-config.yml"
        mock_config.credentials_file = "test-credentials.json"
        mock_config.ingress_rules = []
        mock_config.dns_routing = []
        
        discoverer._tunnel_config = mock_config
        
        with patch.object(discoverer, 'validate_subdomain_routing', return_value={}), \
             patch.object(discoverer, 'test_websocket_connectivity', return_value=[]), \
             patch.object(discoverer, 'get_tunnel_performance_metrics', return_value={}):
            
            report = discoverer.generate_tunnel_report()
            
            assert "discovery_timestamp" in report
            assert "tunnel_configuration" in report
            assert "validation_results" in report
            assert "performance_metrics" in report
            assert "health_status" in report
            assert "module_info" in report

    def test_generate_tunnel_report_no_config(self, discoverer):
        """Test generating tunnel report when no config exists"""
        with patch.object(discoverer, 'discover_tunnel_configuration') as mock_discover:
            mock_config = Mock()
            mock_config.tunnel_id = "test-tunnel"
            mock_config.tunnel_name = "test-tunnel"
            mock_config.status = "active"
            mock_config.config_file = "test-config.yml"
            mock_config.credentials_file = "test-credentials.json"
            mock_config.ingress_rules = []
            mock_config.dns_routing = []
            mock_discover.return_value = mock_config
            
            with patch.object(discoverer, 'validate_subdomain_routing', return_value={}), \
                 patch.object(discoverer, 'test_websocket_connectivity', return_value=[]), \
                 patch.object(discoverer, 'get_tunnel_performance_metrics', return_value={}):
                
                report = discoverer.generate_tunnel_report()
                
                assert report["tunnel_configuration"]["tunnel_id"] == "test-tunnel"
                mock_discover.assert_called_once()

    def test_generate_tunnel_report_error(self, discoverer):
        """Test generating tunnel report with error"""
        with patch.object(discoverer, 'discover_tunnel_configuration', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                discoverer.generate_tunnel_report()

    def test_health_check(self, discoverer):
        """Test health check method"""
        discoverer._tunnel_config = Mock()
        discoverer._tunnel_config.status = "active"
        discoverer._last_discovery_time = datetime.now()
        discoverer._discovery_errors = []
        
        health = discoverer.health_check()
        
        assert "tunnel_discovered" in health
        assert "tunnel_status" in health
        assert "last_discovery" in health
        assert "discovery_errors" in health
        assert "expected_tunnel_id" in health
        assert health["tunnel_discovered"] is True
        assert health["tunnel_status"] == "active"

    def test_service_mappings(self, discoverer):
        """Test service mappings configuration"""
        mappings = discoverer.service_mappings
        
        assert "observatory.nkllon.com" in mappings
        assert mappings["observatory.nkllon.com"]["port"] == 8888
        assert mappings["observatory.nkllon.com"]["service"] == "Observatory"
        
        assert "grafana.observatory.nkllon.com" in mappings
        assert mappings["grafana.observatory.nkllon.com"]["port"] == 3000
        assert mappings["grafana.observatory.nkllon.com"]["service"] == "Grafana"
        
        assert "prometheus.observatory.nkllon.com" in mappings
        assert mappings["prometheus.observatory.nkllon.com"]["port"] == 9090
        assert mappings["prometheus.observatory.nkllon.com"]["service"] == "Prometheus"

    def test_websocket_endpoints(self, discoverer):
        """Test WebSocket endpoints configuration"""
        endpoints = discoverer.websocket_endpoints
        
        assert "/ws/observatory" in endpoints
        assert "/ws/emoji-rain" in endpoints
        assert "/ws/anomalies" in endpoints
        assert "/ws/doctor-status" in endpoints
        assert len(endpoints) == 4


class TestTunnelConfigurationModels:
    """Test suite for tunnel configuration models"""

    def test_tunnel_ingress_rule(self):
        """Test TunnelIngressRule model"""
        rule = TunnelIngressRule(
            hostname="test.example.com",
            service="http://localhost:8080",
            path="/api",
            origin_request={"timeout": "30s"}
        )
        
        assert rule.hostname == "test.example.com"
        assert rule.service == "http://localhost:8080"
        assert rule.path == "/api"
        assert rule.origin_request == {"timeout": "30s"}

    def test_dns_routing(self):
        """Test DNSRouting model"""
        routing = DNSRouting(
            subdomain="test.example.com",
            target_service="TestService",
            port=8080,
            ssl_enabled=True,
            websocket_enabled=True
        )
        
        assert routing.subdomain == "test.example.com"
        assert routing.target_service == "TestService"
        assert routing.port == 8080
        assert routing.ssl_enabled is True
        assert routing.websocket_enabled is True

    def test_tunnel_configuration(self):
        """Test TunnelConfiguration model"""
        ingress_rules = [TunnelIngressRule("test.com", "http://localhost:8080")]
        dns_routing = [DNSRouting("test.com", "TestService", 8080)]
        
        config = TunnelConfiguration(
            tunnel_id="test-tunnel",
            tunnel_name="test-tunnel",
            credentials_file="/test/credentials.json",
            config_file="/test/config.yml",
            ingress_rules=ingress_rules,
            dns_routing=dns_routing,
            status="active",
            last_validated=datetime.now()
        )
        
        assert config.tunnel_id == "test-tunnel"
        assert config.tunnel_name == "test-tunnel"
        assert config.status == "active"
        assert len(config.ingress_rules) == 1
        assert len(config.dns_routing) == 1

    def test_websocket_connectivity_test(self):
        """Test WebSocketConnectivityTest model"""
        test = WebSocketConnectivityTest(
            endpoint="/ws/test",
            accessible=True,
            response_time_ms=50.0,
            error_message=None,
            upgrade_successful=True
        )
        
        assert test.endpoint == "/ws/test"
        assert test.accessible is True
        assert test.response_time_ms == 50.0
        assert test.error_message is None
        assert test.upgrade_successful is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.system_architecture.discovery.cloudflare_tunnel_discoverer"])