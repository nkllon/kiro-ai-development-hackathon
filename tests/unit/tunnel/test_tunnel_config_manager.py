"""
Unit tests for TunnelConfigManager
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.beast_mode.observatory.tunnel.tunnel_config_manager import TunnelConfigManager
from src.beast_mode.observatory.tunnel.websocket_ingress import WebSocketConfig
from src.beast_mode.observatory.tunnel.config_validator import ValidationResult, ValidationLevel
from src.beast_mode.observatory.tunnel.version_manager import VersionStatus
from src.beast_mode.observatory.tunnel.rollback_manager import RollbackReason


class TestTunnelConfigManager:
    """Test TunnelConfigManager functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create manager instance for tests"""
        return TunnelConfigManager(temp_dir)
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for tests"""
        return {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {
                    "hostname": "test.example.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "httpHostHeader": "test.example.com",
                        "proxyType": ""
                    }
                },
                {
                    "service": "http_status:404"
                }
            ]
        }
    
    def test_manager_initialization(self, temp_dir):
        """Test manager initialization"""
        manager = TunnelConfigManager(temp_dir)
        
        assert manager.config_path == Path(temp_dir)
        assert manager.config_path.exists()
        
        # Check that all components are initialized
        assert manager.config_generator is not None
        assert manager.websocket_manager is not None
        assert manager.validator is not None
        assert manager.version_manager is not None
        assert manager.rollback_manager is not None
    
    def test_generate_websocket_config(self, manager):
        """Test WebSocket configuration generation"""
        config = manager.generate_websocket_config(
            tunnel_name="test_tunnel",
            hostname="test.example.com",
            service_url="http://localhost:8080"
        )
        
        # Check basic structure
        assert "tunnel" in config
        assert "credentials-file" in config
        assert "ingress" in config
        
        # Check values
        assert config["tunnel"] == "test_tunnel"
        assert config["credentials-file"] == "/tmp/test_tunnel_credentials.json"
        
        # Check ingress rules
        assert len(config["ingress"]) == 2  # Primary + catch-all
        
        # Check primary rule
        primary_rule = config["ingress"][0]
        assert primary_rule["hostname"] == "test.example.com"
        assert primary_rule["service"] == "http://localhost:8080"
        
        # Check WebSocket support
        origin_request = primary_rule["originRequest"]
        assert origin_request["proxyType"] == ""  # WebSocket enabled
    
    def test_generate_websocket_config_with_custom_websocket_config(self, manager):
        """Test WebSocket configuration generation with custom WebSocket config"""
        websocket_config = WebSocketConfig(
            enabled=True,
            upgrade_timeout=60,
            compression_enabled=False
        )
        
        config = manager.generate_websocket_config(
            tunnel_name="test_tunnel",
            hostname="test.example.com",
            service_url="http://localhost:8080",
            websocket_config=websocket_config
        )
        
        # Should still generate valid config
        assert config["tunnel"] == "test_tunnel"
        assert len(config["ingress"]) == 2
    
    def test_generate_websocket_config_with_custom_credentials(self, manager):
        """Test WebSocket configuration generation with custom credentials file"""
        config = manager.generate_websocket_config(
            tunnel_name="test_tunnel",
            hostname="test.example.com",
            service_url="http://localhost:8080",
            credentials_file="/custom/path/credentials.json"
        )
        
        assert config["credentials-file"] == "/custom/path/credentials.json"
    
    def test_generate_websocket_config_save_to_file_false(self, manager):
        """Test WebSocket configuration generation without saving to file"""
        config = manager.generate_websocket_config(
            tunnel_name="test_tunnel",
            hostname="test.example.com",
            service_url="http://localhost:8080",
            save_to_file=False
        )
        
        # Should still return config
        assert config["tunnel"] == "test_tunnel"
    
    def test_validate_config_valid(self, manager, sample_config):
        """Test configuration validation with valid config"""
        result = manager.validate_config(sample_config)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.critical_errors) == 0
        assert len(result.errors) == 0
    
    def test_validate_config_invalid(self, manager):
        """Test configuration validation with invalid config"""
        invalid_config = {
            "tunnel": 123,  # Invalid type
            "credentials-file": "/tmp/test.json",
            "ingress": []
        }
        
        result = manager.validate_config(invalid_config)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_backup_current_config_valid(self, manager, sample_config):
        """Test backing up valid configuration"""
        version_id = manager.backup_current_config(
            config=sample_config,
            tunnel_name="test_tunnel",
            description="Test backup",
            tags=["test", "backup"]
        )
        
        assert version_id is not None
        assert isinstance(version_id, str)
        
        # Check that version was created
        version_info = manager.version_manager.get_version_info(version_id)
        assert version_info is not None
        assert version_info.tunnel_name == "test_tunnel"
        assert version_info.description == "Test backup"
        assert version_info.tags == ["test", "backup"]
    
    def test_backup_current_config_invalid(self, manager):
        """Test backing up invalid configuration"""
        invalid_config = {
            "tunnel": 123,  # Invalid type
            "credentials-file": "/tmp/test.json",
            "ingress": []
        }
        
        with pytest.raises(ValueError, match="Configuration validation failed"):
            manager.backup_current_config(
                config=invalid_config,
                tunnel_name="test_tunnel"
            )
    
    def test_apply_config_success(self, manager, sample_config):
        """Test successful configuration application"""
        success, version_id = manager.apply_config(
            config=sample_config,
            tunnel_name="test_tunnel",
            create_backup=True,
            validate_before_apply=True
        )
        
        assert success is True
        assert version_id is not None
        
        # Check that version was created and set as active
        version_info = manager.version_manager.get_version_info(version_id)
        assert version_info is not None
        assert version_info.status == VersionStatus.ACTIVE
    
    def test_apply_config_validation_failed(self, manager):
        """Test configuration application with validation failure"""
        invalid_config = {
            "tunnel": 123,  # Invalid type
            "credentials-file": "/tmp/test.json",
            "ingress": []
        }
        
        success, error_msg = manager.apply_config(
            config=invalid_config,
            tunnel_name="test_tunnel",
            validate_before_apply=True
        )
        
        assert success is False
        assert "Configuration validation failed" in error_msg
    
    def test_apply_config_no_backup(self, manager, sample_config):
        """Test configuration application without creating backup"""
        success, version_id = manager.apply_config(
            config=sample_config,
            tunnel_name="test_tunnel",
            create_backup=False,
            validate_before_apply=True
        )
        
        assert success is True
        assert version_id is not None
    
    def test_apply_config_no_validation(self, manager, sample_config):
        """Test configuration application without validation"""
        success, version_id = manager.apply_config(
            config=sample_config,
            tunnel_name="test_tunnel",
            validate_before_apply=False
        )
        
        assert success is True
        assert version_id is not None
    
    def test_rollback_config_to_specific_version(self, manager, sample_config):
        """Test rollback to specific version"""
        # Create a version to rollback to
        version_id = manager.backup_current_config(
            config=sample_config,
            tunnel_name="test_tunnel",
            description="Backup version"
        )
        
        # Apply new config
        manager.apply_config(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        # Rollback to specific version
        success, operation_id = manager.rollback_config(
            tunnel_name="test_tunnel",
            target_version_id=version_id,
            reason=RollbackReason.MANUAL_REQUEST,
            description="Test rollback"
        )
        
        assert success is True
        assert operation_id is not None
    
    def test_rollback_config_to_latest_stable(self, manager, sample_config):
        """Test rollback to latest stable version"""
        # Create a backup version
        manager.backup_current_config(
            config=sample_config,
            tunnel_name="test_tunnel",
            description="Stable version"
        )
        
        # Apply new config
        manager.apply_config(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        # Rollback to latest stable
        success, operation_id = manager.rollback_config(
            tunnel_name="test_tunnel",
            reason=RollbackReason.MANUAL_REQUEST
        )
        
        assert success is True
        assert operation_id is not None
    
    def test_rollback_config_no_target_version(self, manager, sample_config):
        """Test rollback without specifying target version"""
        # Create a backup version
        manager.backup_current_config(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        # Apply new config
        manager.apply_config(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        # Rollback without target version (should use latest stable)
        success, operation_id = manager.rollback_config(
            tunnel_name="test_tunnel",
            reason=RollbackReason.MANUAL_REQUEST
        )
        
        assert success is True
        assert operation_id is not None
    
    def test_get_active_config_existing(self, manager, sample_config):
        """Test getting active configuration when one exists"""
        # Apply config
        manager.apply_config(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        active_config = manager.get_active_config("test_tunnel")
        
        assert active_config is not None
        assert active_config["tunnel"] == "test_tunnel"
    
    def test_get_active_config_nonexistent(self, manager):
        """Test getting active configuration when none exists"""
        active_config = manager.get_active_config("nonexistent_tunnel")
        
        assert active_config is None
    
    def test_list_config_versions(self, manager, sample_config):
        """Test listing configuration versions"""
        # Create multiple versions
        version1 = manager.backup_current_config(
            config=sample_config,
            tunnel_name="test_tunnel",
            description="Version 1"
        )
        version2 = manager.backup_current_config(
            config=sample_config,
            tunnel_name="test_tunnel",
            description="Version 2"
        )
        
        versions = manager.list_config_versions("test_tunnel")
        
        assert len(versions) == 2
        
        # Check version info structure
        for version_info in versions:
            assert "version_id" in version_info
            assert "timestamp" in version_info
            assert "status" in version_info
            assert "description" in version_info
            assert "tags" in version_info
            assert "file_size" in version_info
    
    def test_list_config_versions_with_limit(self, manager, sample_config):
        """Test listing configuration versions with limit"""
        # Create multiple versions
        for i in range(5):
            manager.backup_current_config(
                config=sample_config,
                tunnel_name="test_tunnel",
                description=f"Version {i}"
            )
        
        versions = manager.list_config_versions("test_tunnel", limit=3)
        
        assert len(versions) == 3
    
    def test_get_rollback_history(self, manager, sample_config):
        """Test getting rollback history"""
        # Create a version and rollback
        manager.backup_current_config(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        manager.apply_config(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        manager.rollback_config(
            tunnel_name="test_tunnel",
            reason=RollbackReason.MANUAL_REQUEST
        )
        
        history = manager.get_rollback_history("test_tunnel")
        
        assert len(history) >= 1
        
        # Check rollback operation structure
        rollback_op = history[0]
        assert "operation_id" in rollback_op
        assert "timestamp" in rollback_op
        assert "tunnel_name" in rollback_op
        assert "from_version" in rollback_op
        assert "to_version" in rollback_op
        assert "reason" in rollback_op
        assert "status" in rollback_op
    
    def test_get_rollback_history_with_limit(self, manager, sample_config):
        """Test getting rollback history with limit"""
        # Create multiple rollbacks
        for i in range(3):
            manager.backup_current_config(
                config=sample_config,
                tunnel_name="test_tunnel"
            )
            manager.apply_config(
                config=sample_config,
                tunnel_name="test_tunnel"
            )
            manager.rollback_config(
                tunnel_name="test_tunnel",
                reason=RollbackReason.MANUAL_REQUEST
            )
        
        history = manager.get_rollback_history("test_tunnel", limit=2)
        
        assert len(history) == 2
    
    def test_create_rollback_plan(self, manager, sample_config):
        """Test creating rollback plan"""
        # Create multiple versions
        manager.backup_current_config(
            config=sample_config,
            tunnel_name="test_tunnel",
            description="Version 1"
        )
        manager.backup_current_config(
            config=sample_config,
            tunnel_name="test_tunnel",
            description="Version 2"
        )
        
        # Apply current config
        manager.apply_config(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        plan = manager.create_rollback_plan(
            tunnel_name="test_tunnel",
            reason=RollbackReason.MANUAL_REQUEST,
            description="Test rollback plan"
        )
        
        assert "tunnel_name" in plan
        assert "current_version" in plan
        assert "rollback_reason" in plan
        assert "available_options" in plan
        assert "recommended_option" in plan
        assert "created_at" in plan
        
        assert plan["tunnel_name"] == "test_tunnel"
        assert plan["rollback_reason"] == RollbackReason.MANUAL_REQUEST.value
        assert len(plan["available_options"]) >= 1
    
    def test_emergency_rollback(self, manager, sample_config):
        """Test emergency rollback"""
        # Create a backup version
        manager.backup_current_config(
            config=sample_config,
            tunnel_name="test_tunnel",
            description="Emergency backup"
        )
        
        # Apply new config
        manager.apply_config(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        # Perform emergency rollback
        success, operation_id = manager.emergency_rollback("test_tunnel")
        
        assert success is True
        assert operation_id is not None
    
    def test_emergency_rollback_no_backup(self, manager):
        """Test emergency rollback when no backup exists"""
        success, error_msg = manager.emergency_rollback("nonexistent_tunnel")
        
        assert success is False
        assert "No rollback targets available" in error_msg
    
    def test_get_system_status(self, manager, sample_config):
        """Test getting system status"""
        # Create some versions to have data
        manager.backup_current_config(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        status = manager.get_system_status()
        
        assert "system_ready" in status
        assert "components" in status
        assert "versions" in status
        assert "recent_rollbacks" in status
        assert "config_path" in status
        assert "timestamp" in status
        
        assert status["system_ready"] is True
        
        # Check components
        components = status["components"]
        assert components["config_generator"] is True
        assert components["websocket_manager"] is True
        assert components["validator"] is True
        assert components["version_manager"] is True
        assert components["rollback_manager"] is True
        
        # Check versions
        versions = status["versions"]
        assert "total" in versions
        assert "active" in versions
        assert versions["total"] >= 1
    
    def test_get_system_status_error(self, manager):
        """Test system status when there's an error"""
        # Mock version_manager.list_versions to raise an exception
        with patch.object(manager.version_manager, 'list_versions', side_effect=Exception("Test error")):
            status = manager.get_system_status()
            
            assert status["system_ready"] is False
            assert "error" in status
            assert "Test error" in status["error"]
    
    def test_manager_with_custom_config_path(self, temp_dir):
        """Test manager with custom config path"""
        custom_path = Path(temp_dir) / "custom_configs"
        manager = TunnelConfigManager(str(custom_path))
        
        assert manager.config_path == custom_path
        assert manager.config_path.exists()
    
    def test_manager_error_handling_in_generate_websocket_config(self, manager):
        """Test error handling in generate_websocket_config"""
        # Mock config_generator.generate_websocket_config to raise an exception
        with patch.object(manager.config_generator, 'generate_websocket_config', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                manager.generate_websocket_config(
                    tunnel_name="test_tunnel",
                    hostname="test.example.com",
                    service_url="http://localhost:8080"
                )
    
    def test_manager_error_handling_in_validate_config(self, manager, sample_config):
        """Test error handling in validate_config"""
        # Mock validator.validate_config to raise an exception
        with patch.object(manager.validator, 'validate_config', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                manager.validate_config(sample_config)
    
    def test_manager_error_handling_in_backup_current_config(self, manager, sample_config):
        """Test error handling in backup_current_config"""
        # Mock version_manager.create_version to raise an exception
        with patch.object(manager.version_manager, 'create_version', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                manager.backup_current_config(
                    config=sample_config,
                    tunnel_name="test_tunnel"
                )
    
    def test_manager_error_handling_in_apply_config(self, manager, sample_config):
        """Test error handling in apply_config"""
        # Mock version_manager.create_version to raise an exception
        with patch.object(manager.version_manager, 'create_version', side_effect=Exception("Test error")):
            success, error_msg = manager.apply_config(
                config=sample_config,
                tunnel_name="test_tunnel"
            )
            
            assert success is False
            assert "Test error" in error_msg