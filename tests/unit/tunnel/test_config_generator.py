"""
Unit tests for TunnelConfigGenerator
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from src.beast_mode.observatory.tunnel.config_generator import (
    TunnelConfigGenerator,
    TunnelConfig
)


class TestTunnelConfig:
    """Test TunnelConfig data structure"""
    
    def test_tunnel_config_creation(self):
        """Test basic tunnel config creation"""
        config = TunnelConfig(
            tunnel_name="test_tunnel",
            credentials_file="/tmp/test.json",
            hostname="test.example.com",
            service_url="http://localhost:8080"
        )
        
        assert config.tunnel_name == "test_tunnel"
        assert config.credentials_file == "/tmp/test.json"
        assert config.hostname == "test.example.com"
        assert config.service_url == "http://localhost:8080"
        assert config.websocket_enabled is True  # Default value
    
    def test_tunnel_config_with_websocket_disabled(self):
        """Test tunnel config with WebSocket disabled"""
        config = TunnelConfig(
            tunnel_name="test_tunnel",
            credentials_file="/tmp/test.json",
            hostname="test.example.com",
            service_url="http://localhost:8080",
            websocket_enabled=False
        )
        
        assert config.websocket_enabled is False


class TestTunnelConfigGenerator:
    """Test TunnelConfigGenerator functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir
    
    @pytest.fixture
    def generator(self, temp_dir):
        """Create generator instance for tests"""
        return TunnelConfigGenerator(temp_dir)
    
    @pytest.fixture
    def sample_config(self):
        """Sample tunnel configuration"""
        return TunnelConfig(
            tunnel_name="observatory",
            credentials_file="/tmp/observatory_credentials.json",
            hostname="observatory.nkllon.com",
            service_url="http://localhost:8888"
        )
    
    def test_generator_initialization(self, temp_dir):
        """Test generator initialization"""
        generator = TunnelConfigGenerator(temp_dir)
        
        assert generator.config_dir == Path(temp_dir)
        assert generator.config_dir.exists()
    
    def test_generate_websocket_config(self, generator, sample_config):
        """Test WebSocket configuration generation"""
        config = generator.generate_websocket_config(sample_config)
        
        # Check top-level structure
        assert "tunnel" in config
        assert "credentials-file" in config
        assert "ingress" in config
        
        # Check tunnel name
        assert config["tunnel"] == "observatory"
        assert config["credentials-file"] == "/tmp/observatory_credentials.json"
        
        # Check ingress rules
        assert len(config["ingress"]) == 2  # Primary + catch-all
        
        # Check primary ingress rule
        primary_rule = config["ingress"][0]
        assert primary_rule["hostname"] == "observatory.nkllon.com"
        assert primary_rule["service"] == "http://localhost:8888"
        
        # Check originRequest for WebSocket support
        origin_request = primary_rule["originRequest"]
        assert origin_request["httpHostHeader"] == "observatory.nkllon.com"
        assert origin_request["proxyType"] == ""  # WebSocket upgrade enabled
        assert "connectTimeout" in origin_request
        assert "tlsTimeout" in origin_request
        assert "tcpKeepAlive" in origin_request
        
        # Check catch-all rule
        catch_all_rule = config["ingress"][1]
        assert catch_all_rule["service"] == "http_status:404"
    
    def test_generate_websocket_config_disabled(self, generator):
        """Test configuration generation with WebSocket disabled"""
        config_data = TunnelConfig(
            tunnel_name="test_tunnel",
            credentials_file="/tmp/test.json",
            hostname="test.example.com",
            service_url="http://localhost:8080",
            websocket_enabled=False
        )
        
        config = generator.generate_websocket_config(config_data)
        
        # Check that WebSocket-specific settings are still present
        primary_rule = config["ingress"][0]
        origin_request = primary_rule["originRequest"]
        assert origin_request["proxyType"] == ""  # Still empty for WebSocket support
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.dump')
    def test_generate_config_file(self, mock_yaml_dump, mock_file, generator, sample_config):
        """Test configuration file generation"""
        generator.generate_config_file(sample_config, "test_config.yaml")
        
        # Verify file was opened for writing
        mock_file.assert_called_once()
        
        # Verify YAML dump was called
        mock_yaml_dump.assert_called_once()
    
    def test_generate_minimal_config(self, generator):
        """Test minimal configuration generation"""
        config = generator.generate_minimal_config(
            tunnel_name="minimal_tunnel",
            hostname="minimal.example.com",
            service_url="http://localhost:3000"
        )
        
        assert config["tunnel"] == "minimal_tunnel"
        assert config["credentials-file"] == "/tmp/minimal_tunnel_credentials.json"
        assert len(config["ingress"]) == 2
        
        # Check primary rule
        primary_rule = config["ingress"][0]
        assert primary_rule["hostname"] == "minimal.example.com"
        assert primary_rule["service"] == "http://localhost:3000"
        
        # Check WebSocket support
        origin_request = primary_rule["originRequest"]
        assert origin_request["proxyType"] == ""
    
    def test_validate_generated_config_valid(self, generator, sample_config):
        """Test validation of valid generated config"""
        config = generator.generate_websocket_config(sample_config)
        is_valid = generator.validate_generated_config(config)
        
        assert is_valid is True
    
    def test_validate_generated_config_missing_tunnel(self, generator):
        """Test validation of config missing tunnel field"""
        config = {
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"},
                {"service": "http_status:404"}
            ]
        }
        
        is_valid = generator.validate_generated_config(config)
        assert is_valid is False
    
    def test_validate_generated_config_missing_ingress(self, generator):
        """Test validation of config missing ingress field"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json"
        }
        
        is_valid = generator.validate_generated_config(config)
        assert is_valid is False
    
    def test_validate_generated_config_no_catch_all(self, generator):
        """Test validation of config without catch-all rule"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"}
            ]
        }
        
        is_valid = generator.validate_generated_config(config)
        assert is_valid is False
    
    def test_get_config_template(self, generator):
        """Test getting configuration template"""
        template = generator.get_config_template()
        
        assert "tunnel" in template
        assert "credentials-file" in template
        assert "ingress" in template
        
        # Check template structure
        assert template["tunnel"] == "observatory"
        assert len(template["ingress"]) == 2
        
        # Check WebSocket support in template
        primary_rule = template["ingress"][0]
        origin_request = primary_rule["originRequest"]
        assert origin_request["proxyType"] == ""
    
    def test_config_with_custom_timeouts(self, generator):
        """Test configuration with custom timeout values"""
        config_data = TunnelConfig(
            tunnel_name="custom_tunnel",
            credentials_file="/tmp/custom.json",
            hostname="custom.example.com",
            service_url="http://localhost:9000",
            connect_timeout=60,
            tls_timeout=20,
            tcp_keep_alive=60,
            keep_alive_connections=20,
            keep_alive_timeout=120
        )
        
        config = generator.generate_websocket_config(config_data)
        
        primary_rule = config["ingress"][0]
        origin_request = primary_rule["originRequest"]
        
        assert origin_request["connectTimeout"] == "60s"
        assert origin_request["tlsTimeout"] == "20s"
        assert origin_request["tcpKeepAlive"] == "60s"
        assert origin_request["keepAliveConnections"] == 20
        assert origin_request["keepAliveTimeout"] == "120s"
    
    def test_multiple_hostnames_not_supported(self, generator):
        """Test that generator handles single hostname correctly"""
        config_data = TunnelConfig(
            tunnel_name="single_hostname",
            credentials_file="/tmp/single.json",
            hostname="single.example.com",
            service_url="http://localhost:8080"
        )
        
        config = generator.generate_websocket_config(config_data)
        
        # Should have exactly 2 ingress rules (primary + catch-all)
        assert len(config["ingress"]) == 2
        
        # Primary rule should have the specified hostname
        primary_rule = config["ingress"][0]
        assert primary_rule["hostname"] == "single.example.com"