"""
Unit tests for configuration management.
"""

import os
import pytest
from pathlib import Path
from src.websocket_validation.config import ValidationConfig


class TestValidationConfig:
    """Test cases for ValidationConfig class."""
    
    def test_default_config_creation(self):
        """Test creating config with default values."""
        config = ValidationConfig()
        
        assert config.production_base_url == "https://observatory.nkllon.com"
        assert config.local_base_url == "http://localhost:8888"
        assert config.connection_timeout == 30.0
        assert config.websocket_timeout == 10.0
        assert config.max_retries == 3
        assert config.verify_ssl is True
        assert len(config.websocket_endpoints) > 0
        assert "/ws/emoji-rain" in config.websocket_endpoints
    
    def test_config_from_env(self, monkeypatch):
        """Test creating config from environment variables."""
        monkeypatch.setenv("VALIDATION_PROD_URL", "https://test.example.com")
        monkeypatch.setenv("VALIDATION_LOCAL_URL", "http://localhost:9999")
        monkeypatch.setenv("VALIDATION_TIMEOUT", "60.0")
        monkeypatch.setenv("VALIDATION_MAX_RETRIES", "5")
        monkeypatch.setenv("VALIDATION_VERIFY_SSL", "false")
        
        config = ValidationConfig.from_env()
        
        assert config.production_base_url == "https://test.example.com"
        assert config.local_base_url == "http://localhost:9999"
        assert config.connection_timeout == 60.0
        assert config.max_retries == 5
        assert config.verify_ssl is False
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = ValidationConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "production_base_url" in config_dict
        assert "websocket_endpoints" in config_dict
        assert config_dict["production_base_url"] == config.production_base_url
    
    def test_evidence_directory_creation(self, tmp_path):
        """Test that evidence directory is created."""
        evidence_dir = tmp_path / "test_evidence"
        config = ValidationConfig(evidence_dir=evidence_dir)
        
        assert evidence_dir.exists()
        assert evidence_dir.is_dir()
    
    def test_websocket_endpoints_default(self):
        """Test default WebSocket endpoints are set."""
        config = ValidationConfig()
        
        assert config.websocket_endpoints is not None
        assert isinstance(config.websocket_endpoints, list)
        assert len(config.websocket_endpoints) > 0
        
        expected_endpoints = ["/ws/emoji-rain", "/ws/status", "/ws/health"]
        for endpoint in expected_endpoints:
            assert endpoint in config.websocket_endpoints