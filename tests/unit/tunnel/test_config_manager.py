"""
Unit tests for ConfigManager - WebSocket Tunnel Configuration Management
"""

import json
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open
from src.beast_mode.observatory.tunnel.config_manager import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test-config.yml"
        self.manager = ConfigManager(str(self.config_path))

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test ConfigManager initialization."""
        assert self.manager.config_path == self.config_path
        assert not self.config_path.exists()

    def test_log_action(self, capsys):
        """Test JSON logging functionality."""
        self.manager.log_action("test_action", "completed", {"key": "value"})
        
        captured = capsys.readouterr()
        log_entry = json.loads(captured.out.strip())
        
        assert log_entry["task"] == "1"
        assert log_entry["action"] == "test_action"
        assert log_entry["status"] == "completed"
        assert log_entry["details"]["key"] == "value"
        assert "timestamp" in log_entry

    def test_create_websocket_config_default(self):
        """Test creating WebSocket configuration with default parameters."""
        config = self.manager.create_websocket_config()
        
        assert config["tunnel"] == "observatory"
        assert config["credentials-file"] == "/path/to/credentials.json"
        assert len(config["ingress"]) == 2
        
        # Check WebSocket-enabled ingress rule
        websocket_rule = config["ingress"][0]
        assert websocket_rule["hostname"] == "observatory.nkllon.com"
        assert websocket_rule["service"] == "http://localhost:8888"
        assert websocket_rule["originRequest"]["proxyType"] == ""
        assert websocket_rule["originRequest"]["keepAliveConnections"] == 10
        assert websocket_rule["originRequest"]["keepAliveTimeout"] == "90s"
        
        # Check catch-all rule
        catch_all_rule = config["ingress"][1]
        assert catch_all_rule["service"] == "http_status:404"

    def test_create_websocket_config_custom(self):
        """Test creating WebSocket configuration with custom parameters."""
        config = self.manager.create_websocket_config(
            tunnel_name="test-tunnel",
            hostname="test.example.com",
            local_port=3000,
            credentials_file="/custom/credentials.json"
        )
        
        assert config["tunnel"] == "test-tunnel"
        assert config["credentials-file"] == "/custom/credentials.json"
        
        websocket_rule = config["ingress"][0]
        assert websocket_rule["hostname"] == "test.example.com"
        assert websocket_rule["service"] == "http://localhost:3000"

    def test_save_config_new_file(self):
        """Test saving configuration to new file."""
        config = self.manager.create_websocket_config()
        
        result = self.manager.save_config(config, backup=False)
        
        assert result is True
        assert self.config_path.exists()
        
        # Verify saved content
        with open(self.config_path, 'r') as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config["tunnel"] == config["tunnel"]
        assert len(saved_config["ingress"]) == len(config["ingress"])

    def test_save_config_with_backup(self):
        """Test saving configuration with backup creation."""
        # Create initial config
        config = self.manager.create_websocket_config()
        self.manager.save_config(config, backup=False)
        
        # Modify config
        config["tunnel"] = "modified-tunnel"
        
        # Save with backup
        result = self.manager.save_config(config, backup=True)
        
        assert result is True
        
        # Check backup was created
        backup_files = list(self.config_path.parent.glob("*.backup.*"))
        assert len(backup_files) == 1
        
        # Verify current config is updated
        with open(self.config_path, 'r') as f:
            current_config = yaml.safe_load(f)
        assert current_config["tunnel"] == "modified-tunnel"

    def test_save_config_error(self):
        """Test error handling in save_config."""
        # Create invalid config path
        invalid_manager = ConfigManager("/invalid/path/config.yml")
        
        config = self.manager.create_websocket_config()
        
        # Mock open to raise exception
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            result = invalid_manager.save_config(config)
            assert result is False

    def test_load_config_existing_file(self):
        """Test loading configuration from existing file."""
        # Create and save config
        config = self.manager.create_websocket_config()
        self.manager.save_config(config, backup=False)
        
        # Load config
        loaded_config = self.manager.load_config()
        
        assert loaded_config is not None
        assert loaded_config["tunnel"] == config["tunnel"]
        assert len(loaded_config["ingress"]) == len(config["ingress"])

    def test_load_config_nonexistent_file(self):
        """Test loading configuration from non-existent file."""
        loaded_config = self.manager.load_config()
        assert loaded_config is None

    def test_load_config_invalid_yaml(self):
        """Test loading configuration with invalid YAML."""
        # Create invalid YAML file
        with open(self.config_path, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        loaded_config = self.manager.load_config()
        assert loaded_config is None

    def test_update_websocket_settings_enable(self):
        """Test enabling WebSocket settings."""
        # Create initial config
        config = self.manager.create_websocket_config()
        # Remove WebSocket settings
        config["ingress"][0]["originRequest"].pop("proxyType", None)
        self.manager.save_config(config, backup=False)
        
        # Enable WebSocket
        result = self.manager.update_websocket_settings(enable_websocket=True)
        
        assert result is True
        
        # Verify WebSocket is enabled
        updated_config = self.manager.load_config()
        websocket_rule = updated_config["ingress"][0]
        assert websocket_rule["originRequest"]["proxyType"] == ""
        assert websocket_rule["originRequest"]["keepAliveConnections"] == 10

    def test_update_websocket_settings_disable(self):
        """Test disabling WebSocket settings."""
        # Create config with WebSocket enabled
        config = self.manager.create_websocket_config()
        self.manager.save_config(config, backup=False)
        
        # Disable WebSocket
        result = self.manager.update_websocket_settings(enable_websocket=False)
        
        assert result is True
        
        # Verify WebSocket is disabled
        updated_config = self.manager.load_config()
        websocket_rule = updated_config["ingress"][0]
        assert "proxyType" not in websocket_rule["originRequest"]

    def test_update_websocket_settings_custom_hostname(self):
        """Test updating WebSocket settings for custom hostname."""
        config = {
            "tunnel": "test",
            "ingress": [
                {
                    "hostname": "custom.example.com",
                    "service": "http://localhost:3000",
                    "originRequest": {}
                },
                {"service": "http_status:404"}
            ]
        }
        self.manager.save_config(config, backup=False)
        
        result = self.manager.update_websocket_settings(
            hostname="custom.example.com",
            enable_websocket=True
        )
        
        assert result is True
        
        updated_config = self.manager.load_config()
        custom_rule = updated_config["ingress"][0]
        assert custom_rule["originRequest"]["proxyType"] == ""

    def test_update_websocket_settings_no_config(self):
        """Test updating WebSocket settings when no config exists."""
        result = self.manager.update_websocket_settings()
        assert result is False

    def test_get_config_info_no_file(self):
        """Test getting config info when file doesn't exist."""
        info = self.manager.get_config_info()
        
        assert info["config_path"] == str(self.config_path)
        assert info["exists"] is False
        assert info["websocket_enabled"] is False
        assert info["tunnel_name"] is None
        assert info["hostnames"] == []
        assert info["ingress_count"] == 0

    def test_get_config_info_with_file(self):
        """Test getting config info when file exists."""
        config = self.manager.create_websocket_config()
        self.manager.save_config(config, backup=False)
        
        info = self.manager.get_config_info()
        
        assert info["exists"] is True
        assert info["websocket_enabled"] is True
        assert info["tunnel_name"] == "observatory"
        assert info["hostnames"] == ["observatory.nkllon.com"]
        assert info["ingress_count"] == 2

    def test_get_config_info_websocket_disabled(self):
        """Test getting config info when WebSocket is disabled."""
        config = self.manager.create_websocket_config()
        # Disable WebSocket
        config["ingress"][0]["originRequest"].pop("proxyType", None)
        self.manager.save_config(config, backup=False)
        
        info = self.manager.get_config_info()
        
        assert info["websocket_enabled"] is False

    def test_config_manager_integration(self):
        """Test complete ConfigManager workflow."""
        # Create WebSocket config
        config = self.manager.create_websocket_config(
            tunnel_name="integration-test",
            hostname="integration.example.com",
            local_port=8080
        )
        
        # Save config
        save_result = self.manager.save_config(config, backup=True)
        assert save_result is True
        
        # Load config
        loaded_config = self.manager.load_config()
        assert loaded_config is not None
        assert loaded_config["tunnel"] == "integration-test"
        
        # Update WebSocket settings
        update_result = self.manager.update_websocket_settings(
            hostname="integration.example.com",
            enable_websocket=False
        )
        assert update_result is True
        
        # Verify changes
        final_config = self.manager.load_config()
        websocket_rule = final_config["ingress"][0]
        assert "proxyType" not in websocket_rule["originRequest"]
        
        # Get final info
        info = self.manager.get_config_info()
        assert info["websocket_enabled"] is False
        assert info["tunnel_name"] == "integration-test"