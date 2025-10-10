"""
Unit tests for WebSocketIngressManager
"""

import pytest
from unittest.mock import patch

from src.beast_mode.observatory.tunnel.websocket_ingress import (
    WebSocketIngressManager,
    WebSocketConfig,
    WebSocketMode
)


class TestWebSocketConfig:
    """Test WebSocketConfig data structure"""
    
    def test_websocket_config_defaults(self):
        """Test WebSocket config with default values"""
        config = WebSocketConfig()
        
        assert config.enabled is True
        assert config.upgrade_timeout == 30
        assert config.ping_interval == 30
        assert config.ping_timeout == 10
        assert config.max_message_size == 1048576
        assert config.compression_enabled is True
        assert config.subprotocols == ["websocket"]
    
    def test_websocket_config_custom_values(self):
        """Test WebSocket config with custom values"""
        config = WebSocketConfig(
            enabled=False,
            upgrade_timeout=60,
            ping_interval=45,
            ping_timeout=15,
            max_message_size=2097152,
            compression_enabled=False,
            subprotocols=["custom-protocol", "websocket"]
        )
        
        assert config.enabled is False
        assert config.upgrade_timeout == 60
        assert config.ping_interval == 45
        assert config.ping_timeout == 15
        assert config.max_message_size == 2097152
        assert config.compression_enabled is False
        assert config.subprotocols == ["custom-protocol", "websocket"]


class TestWebSocketIngressManager:
    """Test WebSocketIngressManager functionality"""
    
    @pytest.fixture
    def manager(self):
        """Create manager instance for tests"""
        return WebSocketIngressManager()
    
    @pytest.fixture
    def websocket_config(self):
        """Sample WebSocket configuration"""
        return WebSocketConfig()
    
    def test_manager_initialization(self, manager):
        """Test manager initialization"""
        assert manager is not None
    
    def test_create_websocket_ingress_rule(self, manager, websocket_config):
        """Test WebSocket ingress rule creation"""
        rule = manager.create_websocket_ingress_rule(
            hostname="test.example.com",
            service_url="http://localhost:8080",
            websocket_config=websocket_config
        )
        
        # Check basic structure
        assert "hostname" in rule
        assert "service" in rule
        assert "originRequest" in rule
        
        # Check values
        assert rule["hostname"] == "test.example.com"
        assert rule["service"] == "http://localhost:8080"
        
        # Check originRequest for WebSocket support
        origin_request = rule["originRequest"]
        assert origin_request["httpHostHeader"] == "test.example.com"
        assert origin_request["proxyType"] == ""  # WebSocket upgrade enabled
        assert "connectTimeout" in origin_request
        assert "tlsTimeout" in origin_request
        assert "tcpKeepAlive" in origin_request
        assert "keepAliveConnections" in origin_request
        assert "keepAliveTimeout" in origin_request
    
    def test_create_websocket_ingress_rule_disabled(self, manager):
        """Test ingress rule creation with WebSocket disabled"""
        websocket_config = WebSocketConfig(enabled=False)
        
        rule = manager.create_websocket_ingress_rule(
            hostname="test.example.com",
            service_url="http://localhost:8080",
            websocket_config=websocket_config
        )
        
        # Should still have basic structure
        assert rule["hostname"] == "test.example.com"
        assert rule["service"] == "http://localhost:8080"
        
        # OriginRequest should still be present
        assert "originRequest" in rule
        origin_request = rule["originRequest"]
        assert origin_request["proxyType"] == ""  # Still empty for WebSocket support
    
    def test_create_websocket_ingress_rule_with_headers(self, manager, websocket_config):
        """Test ingress rule creation with additional headers"""
        additional_headers = {
            "X-Custom-Header": "custom-value",
            "Authorization": "Bearer token"
        }
        
        rule = manager.create_websocket_ingress_rule(
            hostname="test.example.com",
            service_url="http://localhost:8080",
            websocket_config=websocket_config,
            additional_headers=additional_headers
        )
        
        # Check that additional headers are included
        assert "websocketHeaders" in rule
        websocket_headers = rule["websocketHeaders"]
        
        # Should have WebSocket headers plus additional headers
        assert "Connection" in websocket_headers
        assert "Upgrade" in websocket_headers
        assert "Sec-WebSocket-Version" in websocket_headers
        assert "X-Custom-Header" in websocket_headers
        assert "Authorization" in websocket_headers
    
    def test_create_websocket_ingress_rule_compression_disabled(self, manager):
        """Test ingress rule creation with compression disabled"""
        websocket_config = WebSocketConfig(compression_enabled=False)
        
        rule = manager.create_websocket_ingress_rule(
            hostname="test.example.com",
            service_url="http://localhost:8080",
            websocket_config=websocket_config
        )
        
        # Check that compression header is not included
        assert "websocketHeaders" in rule
        websocket_headers = rule["websocketHeaders"]
        
        # Should not have compression extension
        assert "Sec-WebSocket-Extensions" not in websocket_headers
    
    def test_create_websocket_ingress_rule_custom_subprotocols(self, manager):
        """Test ingress rule creation with custom subprotocols"""
        websocket_config = WebSocketConfig(subprotocols=["custom-protocol", "websocket"])
        
        rule = manager.create_websocket_ingress_rule(
            hostname="test.example.com",
            service_url="http://localhost:8080",
            websocket_config=websocket_config
        )
        
        # Check subprotocol header
        assert "websocketHeaders" in rule
        websocket_headers = rule["websocketHeaders"]
        
        assert "Sec-WebSocket-Protocol" in websocket_headers
        assert websocket_headers["Sec-WebSocket-Protocol"] == "custom-protocol, websocket"
    
    def test_create_websocket_catch_all_rule(self, manager):
        """Test catch-all rule creation"""
        rule = manager.create_websocket_catch_all_rule()
        
        assert rule["service"] == "http_status:404"
        assert len(rule) == 1  # Should only have service field
    
    def test_create_websocket_tunnel_config(self, manager, websocket_config):
        """Test complete WebSocket tunnel configuration creation"""
        config = manager.create_websocket_tunnel_config(
            tunnel_name="websocket_tunnel",
            credentials_file="/tmp/websocket_credentials.json",
            hostname="websocket.example.com",
            service_url="http://localhost:8080",
            websocket_config=websocket_config
        )
        
        # Check top-level structure
        assert "tunnel" in config
        assert "credentials-file" in config
        assert "ingress" in config
        
        # Check values
        assert config["tunnel"] == "websocket_tunnel"
        assert config["credentials-file"] == "/tmp/websocket_credentials.json"
        
        # Check ingress rules
        assert len(config["ingress"]) == 2  # Primary + catch-all
        
        # Check primary rule
        primary_rule = config["ingress"][0]
        assert primary_rule["hostname"] == "websocket.example.com"
        assert primary_rule["service"] == "http://localhost:8080"
        
        # Check catch-all rule
        catch_all_rule = config["ingress"][1]
        assert catch_all_rule["service"] == "http_status:404"
    
    def test_validate_websocket_ingress_valid(self, manager, websocket_config):
        """Test validation of valid WebSocket ingress rule"""
        rule = manager.create_websocket_ingress_rule(
            hostname="test.example.com",
            service_url="http://localhost:8080",
            websocket_config=websocket_config
        )
        
        is_valid = manager.validate_websocket_ingress(rule)
        assert is_valid is True
    
    def test_validate_websocket_ingress_missing_hostname(self, manager):
        """Test validation of ingress rule missing hostname"""
        rule = {
            "service": "http://localhost:8080",
            "originRequest": {
                "proxyType": ""
            }
        }
        
        is_valid = manager.validate_websocket_ingress(rule)
        assert is_valid is False
    
    def test_validate_websocket_ingress_missing_service(self, manager):
        """Test validation of ingress rule missing service"""
        rule = {
            "hostname": "test.example.com",
            "originRequest": {
                "proxyType": ""
            }
        }
        
        is_valid = manager.validate_websocket_ingress(rule)
        assert is_valid is False
    
    def test_validate_websocket_ingress_missing_origin_request(self, manager):
        """Test validation of ingress rule missing originRequest"""
        rule = {
            "hostname": "test.example.com",
            "service": "http://localhost:8080"
        }
        
        is_valid = manager.validate_websocket_ingress(rule)
        assert is_valid is False
    
    def test_validate_websocket_ingress_invalid_proxy_type(self, manager):
        """Test validation of ingress rule with invalid proxyType"""
        rule = {
            "hostname": "test.example.com",
            "service": "http://localhost:8080",
            "originRequest": {
                "proxyType": "http"  # Should be empty for WebSocket
            }
        }
        
        is_valid = manager.validate_websocket_ingress(rule)
        assert is_valid is False
    
    def test_get_websocket_headers_template(self, manager):
        """Test getting WebSocket headers template"""
        template = manager.get_websocket_headers_template()
        
        assert "Connection" in template
        assert "Upgrade" in template
        assert "Sec-WebSocket-Version" in template
        assert "Sec-WebSocket-Extensions" in template
        assert "Sec-WebSocket-Protocol" in template
        
        # Check values
        assert template["Connection"] == "Upgrade"
        assert template["Upgrade"] == "websocket"
        assert template["Sec-WebSocket-Version"] == "13"
        assert template["Sec-WebSocket-Extensions"] == "permessage-deflate"
        assert template["Sec-WebSocket-Protocol"] == "websocket"
    
    def test_create_multiple_websocket_rules(self, manager, websocket_config):
        """Test creation of multiple WebSocket ingress rules"""
        rules_config = [
            {
                "hostname": "app1.example.com",
                "service_url": "http://localhost:8080",
                "additional_headers": {"X-App": "app1"}
            },
            {
                "hostname": "app2.example.com",
                "service_url": "http://localhost:8081",
                "additional_headers": {"X-App": "app2"}
            }
        ]
        
        ingress_rules = manager.create_multiple_websocket_rules(
            rules_config, websocket_config
        )
        
        # Should have 2 primary rules + 1 catch-all = 3 total
        assert len(ingress_rules) == 3
        
        # Check first rule
        rule1 = ingress_rules[0]
        assert rule1["hostname"] == "app1.example.com"
        assert rule1["service"] == "http://localhost:8080"
        
        # Check second rule
        rule2 = ingress_rules[1]
        assert rule2["hostname"] == "app2.example.com"
        assert rule2["service"] == "http://localhost:8081"
        
        # Check catch-all rule
        catch_all = ingress_rules[2]
        assert catch_all["service"] == "http_status:404"
    
    def test_websocket_config_with_custom_timeouts(self, manager):
        """Test WebSocket config with custom timeout values"""
        websocket_config = WebSocketConfig(
            upgrade_timeout=60,
            ping_interval=45,
            ping_timeout=15
        )
        
        rule = manager.create_websocket_ingress_rule(
            hostname="test.example.com",
            service_url="http://localhost:8080",
            websocket_config=websocket_config
        )
        
        origin_request = rule["originRequest"]
        assert origin_request["connectTimeout"] == "60s"
    
    def test_websocket_config_with_max_message_size(self, manager):
        """Test WebSocket config with custom max message size"""
        websocket_config = WebSocketConfig(max_message_size=2097152)
        
        rule = manager.create_websocket_ingress_rule(
            hostname="test.example.com",
            service_url="http://localhost:8080",
            websocket_config=websocket_config
        )
        
        # Max message size is not directly used in ingress rules
        # but config should be created successfully
        assert rule["hostname"] == "test.example.com"
        assert rule["service"] == "http://localhost:8080"