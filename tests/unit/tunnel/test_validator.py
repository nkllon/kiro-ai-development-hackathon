"""
Unit tests for ConfigValidator - Tunnel Configuration Validation
"""

import json
import pytest
from unittest.mock import patch
from src.beast_mode.observatory.tunnel.validator import TunnelValidator, ValidationError


class TestTunnelValidator:
    """Test cases for TunnelValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = TunnelValidator()

    def test_init(self):
        """Test TunnelValidator initialization."""
        assert self.validator is not None
        assert self.validator.REQUIRED_FIELDS == ["tunnel", "ingress"]
        assert self.validator.WEBSOCKET_PROXY_TYPE == ""

    def test_log_action(self, capsys):
        """Test JSON logging functionality."""
        self.validator.log_action("test_action", "completed", {"key": "value"})
        
        captured = capsys.readouterr()
        log_entry = json.loads(captured.out.strip())
        
        assert log_entry["task"] == "1"
        assert log_entry["action"] == "test_action"
        assert log_entry["status"] == "completed"
        assert log_entry["details"]["key"] == "value"
        assert "timestamp" in log_entry

    def test_validate_config_valid_websocket(self):
        """Test validation of valid WebSocket configuration."""
        config = {
            "tunnel": "test-tunnel",
            "credentials-file": "/path/to/credentials.json",
            "ingress": [
                {
                    "hostname": "test.example.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "proxyType": "",
                        "keepAliveConnections": 10,
                        "keepAliveTimeout": "90s",
                        "connectTimeout": "30s",
                        "tlsTimeout": "10s"
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_config_missing_required_fields(self):
        """Test validation with missing required fields."""
        config = {
            "ingress": [{"service": "http_status:404"}]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("Required field 'tunnel' is missing" in error for error in errors)

    def test_validate_config_invalid_tunnel_name(self):
        """Test validation with invalid tunnel name."""
        config = {
            "tunnel": "invalid_tunnel_name!",
            "ingress": [{"service": "http_status:404"}]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("Tunnel name must contain only alphanumeric characters and hyphens" in error for error in errors)

    def test_validate_config_invalid_ingress_structure(self):
        """Test validation with invalid ingress structure."""
        config = {
            "tunnel": "test",
            "ingress": "not_a_list"
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("Ingress must be a list" in error for error in errors)

    def test_validate_config_empty_ingress(self):
        """Test validation with empty ingress list."""
        config = {
            "tunnel": "test",
            "ingress": []
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("At least one ingress rule is required" in error for error in errors)

    def test_validate_config_last_rule_has_hostname(self):
        """Test validation when last rule has hostname."""
        config = {
            "tunnel": "test",
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"},
                {"hostname": "another.com", "service": "http://localhost:8080"}
            ]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("Last ingress rule must be a catch-all" in error for error in errors)

    def test_validate_config_duplicate_hostnames(self):
        """Test validation with duplicate hostnames."""
        config = {
            "tunnel": "test",
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"},
                {"hostname": "test.com", "service": "http://localhost:8080"},
                {"service": "http_status:404"}
            ]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("Duplicate hostname 'test.com'" in error for error in errors)

    def test_validate_config_invalid_service_type(self):
        """Test validation with invalid service type."""
        config = {
            "tunnel": "test",
            "ingress": [
                {"service": "invalid://service"},
                {"service": "http_status:404"}
            ]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("Invalid service type" in error for error in errors)

    def test_validate_config_invalid_hostname_format(self):
        """Test validation with invalid hostname format."""
        config = {
            "tunnel": "test",
            "ingress": [
                {"hostname": "invalid..hostname", "service": "http://localhost:8080"},
                {"service": "http_status:404"}
            ]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("consecutive dots" in error for error in errors)

    def test_validate_config_invalid_timeout_format(self):
        """Test validation with invalid timeout format."""
        config = {
            "tunnel": "test",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "connectTimeout": "invalid_timeout"
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("Invalid connectTimeout format" in error for error in errors)

    def test_validate_config_timeout_too_high(self):
        """Test validation with timeout values too high."""
        config = {
            "tunnel": "test",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "connectTimeout": "400s"  # Exceeds MAX_CONNECT_TIMEOUT
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("exceeds maximum" in error for error in errors)

    def test_validate_config_websocket_missing_settings(self):
        """Test validation of WebSocket configuration missing recommended settings."""
        config = {
            "tunnel": "test",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "proxyType": ""  # WebSocket enabled but missing keep-alive settings
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("should specify keepAliveConnections" in error for error in errors)
        assert any("should specify keepAliveTimeout" in error for error in errors)

    def test_validate_config_websocket_invalid_service(self):
        """Test validation of WebSocket configuration with invalid service."""
        config = {
            "tunnel": "test",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "ssh://localhost:22",  # SSH service with WebSocket
                    "originRequest": {
                        "proxyType": "",
                        "keepAliveConnections": 10,
                        "keepAliveTimeout": "90s"
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("service must be HTTP/HTTPS for WebSocket upgrade" in error for error in errors)

    def test_validate_config_missing_credentials(self):
        """Test validation with missing credentials file."""
        config = {
            "tunnel": "test",
            "ingress": [
                {"service": "http_status:404"}
            ]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("Missing credentials-file" in error for error in errors)

    def test_validate_config_tls_timeout_too_low(self):
        """Test validation with TLS timeout too low."""
        config = {
            "tunnel": "test",
            "credentials-file": "/path/to/credentials.json",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "tlsTimeout": "2s"  # Too low for secure connections
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("TLS timeout is too low" in error for error in errors)

    def test_validate_config_http_external_service(self):
        """Test validation warning for HTTP external service."""
        config = {
            "tunnel": "test",
            "credentials-file": "/path/to/credentials.json",
            "ingress": [
                {
                    "hostname": "external.com",
                    "service": "http://external.com:8080",  # HTTP for external service
                    "originRequest": {}
                },
                {"service": "http_status:404"}
            ]
        }
        
        is_valid, errors = self.validator.validate_config(config)
        
        assert is_valid is False
        assert any("uses HTTP for external service" in error for error in errors)

    def test_validate_yaml_syntax_valid(self):
        """Test YAML syntax validation with valid YAML."""
        yaml_content = """
tunnel: test-tunnel
ingress:
  - hostname: test.com
    service: http://localhost:8080
  - service: http_status:404
"""
        
        is_valid, error_msg = self.validator.validate_yaml_syntax(yaml_content)
        
        assert is_valid is True
        assert error_msg is None

    def test_validate_yaml_syntax_invalid(self):
        """Test YAML syntax validation with invalid YAML."""
        yaml_content = """
tunnel: test-tunnel
ingress:
  - hostname: test.com
    service: http://localhost:8080
  - service: http_status:404
    invalid: [unclosed
"""
        
        is_valid, error_msg = self.validator.validate_yaml_syntax(yaml_content)
        
        assert is_valid is False
        assert "YAML syntax error" in error_msg

    def test_get_validation_summary(self):
        """Test getting validation summary."""
        config = {
            "tunnel": "test-tunnel",
            "credentials-file": "/path/to/credentials.json",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "proxyType": "",
                        "keepAliveConnections": 10,
                        "keepAliveTimeout": "90s"
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        summary = self.validator.get_validation_summary(config)
        
        assert "is_valid" in summary
        assert "error_count" in summary
        assert "errors" in summary
        assert "tunnel_name" in summary
        assert "ingress_rules_count" in summary
        assert "websocket_rules_count" in summary
        assert "has_credentials" in summary
        assert "validation_timestamp" in summary
        
        assert summary["tunnel_name"] == "test-tunnel"
        assert summary["ingress_rules_count"] == 2
        assert summary["websocket_rules_count"] == 1
        assert summary["has_credentials"] is True

    def test_validate_config_exception_handling(self):
        """Test exception handling in validation."""
        # Mock _validate_basic_structure to raise exception
        with patch.object(self.validator, '_validate_basic_structure', side_effect=Exception("Test exception")):
            config = {"tunnel": "test"}
            
            is_valid, errors = self.validator.validate_config(config)
            
            assert is_valid is False
            assert any("Validation failed with exception" in error for error in errors)

    def test_parse_timeout_seconds(self):
        """Test timeout parsing functionality."""
        # Valid timeouts
        assert self.validator._parse_timeout_seconds("30s") == 30
        assert self.validator._parse_timeout_seconds("5m") == 300
        assert self.validator._parse_timeout_seconds("1h") == 3600
        
        # Invalid timeouts
        assert self.validator._parse_timeout_seconds("invalid") == 0
        assert self.validator._parse_timeout_seconds("") == 0
        assert self.validator._parse_timeout_seconds(None) == 0

    def test_validator_integration(self):
        """Test complete validator workflow."""
        # Test valid WebSocket configuration
        valid_config = {
            "tunnel": "integration-test",
            "credentials-file": "/path/to/credentials.json",
            "ingress": [
                {
                    "hostname": "integration.example.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "proxyType": "",
                        "keepAliveConnections": 10,
                        "keepAliveTimeout": "90s",
                        "connectTimeout": "30s",
                        "tlsTimeout": "10s",
                        "httpHostHeader": "integration.example.com"
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        # Validate configuration
        is_valid, errors = self.validator.validate_config(valid_config)
        assert is_valid is True
        assert len(errors) == 0
        
        # Validate YAML syntax
        yaml_content = """
tunnel: integration-test
credentials-file: /path/to/credentials.json
ingress:
  - hostname: integration.example.com
    service: http://localhost:8080
    originRequest:
      proxyType: ""
      keepAliveConnections: 10
      keepAliveTimeout: 90s
      connectTimeout: 30s
      tlsTimeout: 10s
      httpHostHeader: integration.example.com
  - service: http_status:404
"""
        
        is_yaml_valid, yaml_error = self.validator.validate_yaml_syntax(yaml_content)
        assert is_yaml_valid is True
        assert yaml_error is None
        
        # Get validation summary
        summary = self.validator.get_validation_summary(valid_config)
        assert summary["is_valid"] is True
        assert summary["websocket_rules_count"] == 1
        assert summary["has_credentials"] is True